// Authentication and NextAuth Type Definitions

export interface GitHubProfile {
  id: number;
  email: string;
  name: string;
  avatar_url: string;
  login: string;
  company?: string | null;
  location?: string | null;
  bio?: string | null;
  public_repos: number;
  followers: number;
  following: number;
}

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  image?: string;
  github_id?: number;
  avatar_url?: string;
  tier?: "free" | "pro" | "team" | "enterprise";
  tokens_used_today?: number;
  is_active?: boolean;
  is_verified?: boolean;
}

export interface ExtendedUser extends AuthUser {
  access_token?: string;
  refresh_token?: string;
  user?: AuthUser;
}

export interface AuthAccount {
  access_token: string;
  expires_at: number;
  refresh_token?: string;
  scope: string;
  token_type: string;
  type: string;
  provider: string;
  providerAccountId: string;
  userId?: string;
}

export interface AuthSession {
  user: AuthUser;
  expires: string;
  access_token?: string;
  refresh_token?: string;
  error?: string;
}

export interface ExtendedSession extends AuthSession {
  error?: "RefreshAccessTokenError" | "AuthenticationError";
}

export interface AuthToken extends AuthUser {
  access_token?: string;
  refresh_token?: string;
  exp?: number;
  iat?: number;
  error?: "RefreshAccessTokenError" | "AuthenticationError";
}

export interface AuthCallbacks {
  signIn: (params: {
    user: AuthUser;
    account: AuthAccount | null;
    profile?: GitHubProfile;
  }) => Promise<boolean>;

  jwt: (params: {
    token: AuthToken;
    user?: ExtendedUser;
    account?: AuthAccount;
  }) => Promise<AuthToken>;

  session: (params: {
    session: AuthSession;
    token: AuthToken;
  }) => Promise<ExtendedSession>;
}

export interface NextAuthConfig {
  providers: any[];
  callbacks: AuthCallbacks;
  pages: {
    signIn: string;
    error: string;
  };
  session: {
    strategy: "jwt";
  };
  secret: string;
}
