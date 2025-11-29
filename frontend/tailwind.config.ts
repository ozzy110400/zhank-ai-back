import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./pages/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          light: "hsl(var(--primary-light))",
          dark: "hsl(var(--primary-dark))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
          light: "hsl(var(--accent-light))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: {
            height: "0",
          },
          to: {
            height: "var(--radix-accordion-content-height)",
          },
        },
        "accordion-up": {
          from: {
            height: "var(--radix-accordion-content-height)",
          },
          to: {
            height: "0",
          },
        },
        "glow-pulse": {
          "0%, 100%": {
            boxShadow: "0 0 20px hsl(var(--primary) / 0.4), 0 0 40px hsl(var(--primary) / 0.2)",
            borderColor: "hsl(var(--primary) / 0.5)",
          },
          "50%": {
            boxShadow: "0 0 30px hsl(var(--primary) / 0.6), 0 0 60px hsl(var(--primary) / 0.3)",
            borderColor: "hsl(var(--primary) / 0.8)",
          },
        },
        "zap-bounce": {
          "0%, 100%": {
            transform: "translateY(0) scale(1)",
          },
          "25%": {
            transform: "translateY(-2px) scale(1.05)",
          },
          "50%": {
            transform: "translateY(0) scale(1)",
          },
          "75%": {
            transform: "translateY(1px) scale(0.98)",
          },
        },
        "icon-glow": {
          "0%, 100%": {
            filter: "drop-shadow(0 0 4px hsl(var(--primary) / 0.6))",
          },
          "50%": {
            filter: "drop-shadow(0 0 12px hsl(var(--primary) / 0.9))",
          },
        },
        "typewriter-loop": {
          "0%": {
            width: "0",
          },
          "40%": {
            width: "8ch",
          },
          "60%": {
            width: "8ch",
          },
          "100%": {
            width: "0",
          },
        },
        "blink-caret": {
          "0%, 100%": {
            borderColor: "transparent",
          },
          "50%": {
            borderColor: "hsl(var(--primary))",
          },
        },
        "fade-in-up": {
          "0%": {
            opacity: "0",
            transform: "translateY(20px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
        "wave": {
          "0%": { transform: "rotate(0deg)" },
          "10%": { transform: "rotate(14deg)" },
          "20%": { transform: "rotate(-8deg)" },
          "30%": { transform: "rotate(14deg)" },
          "40%": { transform: "rotate(-4deg)" },
          "50%": { transform: "rotate(10deg)" },
          "60%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(0deg)" },
        },
        "float": {
          "0%, 100%": {
            transform: "translateY(0)",
          },
          "50%": {
            transform: "translateY(-6px)",
          },
        },
        "pop-in": {
          "0%": {
            opacity: "0",
            transform: "scale(0.8)",
          },
          "70%": {
            transform: "scale(1.05)",
          },
          "100%": {
            opacity: "1",
            transform: "scale(1)",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "zap-bounce": "zap-bounce 2s ease-in-out infinite",
        "icon-glow": "icon-glow 2s ease-in-out infinite",
        "typewriter-loop": "typewriter-loop 4s steps(8) infinite",
        "blink-caret": "blink-caret 0.75s step-end infinite",
        "fade-in-up": "fade-in-up 0.6s ease-out forwards",
        "fade-in-up-delay-1": "fade-in-up 0.6s ease-out 0.3s forwards",
        "fade-in-up-delay-2": "fade-in-up 0.6s ease-out 0.6s forwards",
        "wave": "wave 2s ease-in-out infinite",
        "float": "float 3s ease-in-out infinite",
        "pop-in": "pop-in 0.4s ease-out forwards",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
