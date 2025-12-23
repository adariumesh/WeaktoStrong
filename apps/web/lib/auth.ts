import { AuthOptions } from "next-auth";
import { JWT } from "next-auth/jwt";
import CredentialsProvider from "next-auth/providers/credentials";
import GitHubProvider from "next-auth/providers/github";
import { GitHubProfile, ExtendedUser, AuthToken } from "./types/auth";

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  tier: "free" | "pro" | "team" | "enterprise";
  tokens_used_today: number;
  is_active: boolean;
  is_verified: boolean;
}

// Extend NextAuth types
declare module "next-auth" {
  interface Session {
    user: User & {
      access_token: string;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    user: User;
    access_token: string;
    refresh_token: string;
  }
}

async function refreshAccessToken(token: JWT): Promise<JWT> {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh_token: token.refresh_token,
        }),
      }
    );

    const refreshedTokens = await response.json();

    if (!response.ok) {
      throw refreshedTokens;
    }

    return {
      ...token,
      access_token: refreshedTokens.access_token,
      refresh_token: refreshedTokens.refresh_token ?? token.refresh_token,
      user: refreshedTokens.user,
    };
  } catch (error) {
    console.error("Error refreshing access token", error);
    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
}

export const authOptions: AuthOptions = {
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                email: credentials.email,
                password: credentials.password,
              }),
            }
          );

          const data = await response.json();

          if (!response.ok) {
            return null;
          }

          return {
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            image: data.user.avatar_url,
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            user: data.user,
          };
        } catch (error) {
          console.error("Auth error:", error);
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Handle OAuth sign in
      if (account?.provider === "github") {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/oauth/github`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                github_id: (profile as GitHubProfile)?.id,
                email: (profile as GitHubProfile)?.email,
                name: (profile as GitHubProfile)?.name,
                avatar_url: (profile as GitHubProfile)?.avatar_url,
              }),
            }
          );

          const data = await response.json();

          if (response.ok) {
            // Store tokens for JWT callback
            const extendedUser = user as ExtendedUser;
            extendedUser.access_token = data.access_token;
            extendedUser.refresh_token = data.refresh_token;
            extendedUser.user = data.user;
            return true;
          }
        } catch (error) {
          console.error("OAuth error:", error);
          return false;
        }
      }

      return true;
    },
    async jwt({ token, user, account }): Promise<JWT> {
      // Initial sign in
      if (account && user) {
        const extendedUser = user as ExtendedUser;
        return {
          ...token,
          access_token: extendedUser.access_token || "",
          refresh_token: extendedUser.refresh_token || "",
          user: extendedUser.user
            ? {
                ...extendedUser.user,
                tier: extendedUser.user.tier || ("free" as const),
                tokens_used_today: extendedUser.user.tokens_used_today || 0,
                is_active: extendedUser.user.is_active ?? true,
                is_verified: extendedUser.user.is_verified ?? false,
              }
            : {
                ...extendedUser,
                tier: "free" as const,
                tokens_used_today: 0,
                is_active: true,
                is_verified: false,
              },
        };
      }

      // Return previous token if the access token has not expired yet
      const currentTime = Date.now();
      const expTimestamp = token.exp;
      if (
        typeof expTimestamp === "number" &&
        currentTime < expTimestamp * 1000
      ) {
        return token;
      }

      // Access token has expired, try to update it
      return refreshAccessToken(token);
    },
    async session({ session, token }) {
      if (token.error) {
        // Force sign out if refresh failed
        const extendedSession = session as any;
        extendedSession.error = "RefreshAccessTokenError";
        return session;
      }

      session.user = {
        ...(token.user || token),
        access_token: token.access_token,
      };

      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
};
