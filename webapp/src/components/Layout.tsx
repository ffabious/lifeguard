import { Outlet, useLocation, Link } from "react-router-dom";
import { Home, Dumbbell, Apple, ShoppingCart, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/workouts", icon: Dumbbell, label: "Workouts" },
    { path: "/nutrition", icon: Apple, label: "Nutrition" },
    { path: "/shopping", icon: ShoppingCart, label: "Shopping" },
    { path: "/settings", icon: Settings, label: "Settings" },
];

export default function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen flex flex-col bg-background">
            {/* Main content */}
            <main className="flex-1 pb-20 px-4 py-4">
                <Outlet />
            </main>

            {/* Bottom navigation */}
            <nav className="fixed bottom-0 left-0 right-0 bg-background border-t">
                <div className="flex justify-around items-center h-16">
                    {navItems.map(({ path, icon: Icon, label }) => {
                        const isActive = location.pathname === path;
                        return (
                            <Link
                                key={path}
                                to={path}
                                className={cn(
                                    "flex flex-col items-center justify-center w-full h-full",
                                    "transition-colors",
                                    isActive
                                        ? "text-primary"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                <Icon className="h-5 w-5" />
                                <span className="text-xs mt-1">{label}</span>
                            </Link>
                        );
                    })}
                </div>
            </nav>
        </div>
    );
}
