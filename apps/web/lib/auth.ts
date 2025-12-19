import { AuthOptions } from "next-auth";
import { JWT } from "next-auth/jwt";
import CredentialsProvider from "next-auth/providers/credentials";
import GitHubProvider from "next-auth/providers/github";

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
                github_id: (profile as any)?.id,
                email: (profile as any)?.email,
                name: (profile as any)?.name,
                avatar_url: (profile as any)?.avatar_url,
              }),
            }
          );

          const data = await response.json();

          if (response.ok) {
            // Store tokens for JWT callback
            (user as any).access_token = data.access_token;
            (user as any).refresh_token = data.refresh_token;
            (user as any).user = data.user;
            return true;
          }
        } catch (error) {
          console.error("OAuth error:", error);
          return false;
        }
      }

      return true;
    },
    async jwt({ token, user, account }) {
      // Initial sign in
      if (account && user) {
        return {
          access_token: (user as any).access_token,
          refresh_token: (user as any).refresh_token,
          user: (user as any).user,
        };
      }

      // Return previous token if the access token has not expired yet
      if (Date.now() < (token as any).exp * 1000) {
        return token;
      }

      // Access token has expired, try to update it
      return refreshAccessToken(token);
    },
    async session({ session, token }) {
      if ((token as any).error) {
        // Force sign out if refresh failed
        (session as any).error = "RefreshAccessTokenError";
        return session;
      }

      session.user = {
        ...(token.user as any),
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
