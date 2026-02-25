import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { getDbClient } from "@/lib/db-adapter";
import bcrypt from "bcryptjs";

export const { handlers, auth, signIn, signOut } = NextAuth({
    providers: [
        Credentials({
            name: "Odiseo",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" },
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) return null;

                const db = await getDbClient();
                const user = await db.get("SELECT * FROM users WHERE email = $1 OR email = ?", [credentials.email, credentials.email]) as any;

                if (db.type === 'sqlite') await (db as any).close();
                else await (db as any).close();

                if (user && user.password_hash) {
                    const isValid = await bcrypt.compare(credentials.password as string, user.password_hash);
                    if (isValid) {
                        return { id: user.id, email: user.email, name: user.email.split('@')[0] };
                    }
                }
                return null;
            },
        }),
    ],
    callbacks: {
        async session({ session, token }) {
            if (token.sub) {
                session.user.id = token.sub;

                const db = await getDbClient();
                const sub = await db.get("SELECT tier, status FROM subscriptions WHERE user_id = $1 OR user_id = ?", [token.sub, token.sub]) as any;
                await db.close();

                if (sub) {
                    (session.user as any).tier = sub.tier;
                    (session.user as any).isVip = sub.status === 'active' && (sub.tier === 'vip_telegram' || sub.tier === 'mercado_pro');
                    (session.user as any).isPro = sub.status === 'active' && sub.tier === 'mercado_pro';
                } else {
                    (session.user as any).tier = 'free';
                }
            }
            return session;
        },
        async jwt({ token, user }) {
            if (user) {
                token.id = user.id;
            }
            return token;
        }
    },
    pages: {
        signIn: "/login",
    },
    session: {
        strategy: "jwt",
    },
});
