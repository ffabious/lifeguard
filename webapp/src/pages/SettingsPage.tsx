import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, UserGoals } from "@/lib/api";
import { useTelegram } from "@/hooks/useTelegram";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SettingsPage() {
    const { user, webApp } = useTelegram();
    const queryClient = useQueryClient();

    const { data: currentUser } = useQuery({
        queryKey: ["user"],
        queryFn: () => api.getCurrentUser(),
    });

    const [goals, setGoals] = useState<UserGoals>({
        daily_calorie_goal: 2000,
        daily_protein_goal: 150,
        daily_carbs_goal: 250,
        daily_fat_goal: 65,
        daily_water_goal: 8,
    });

    useEffect(() => {
        if (currentUser) {
            setGoals({
                daily_calorie_goal: currentUser.daily_calorie_goal,
                daily_protein_goal: currentUser.daily_protein_goal,
                daily_carbs_goal: currentUser.daily_carbs_goal,
                daily_fat_goal: currentUser.daily_fat_goal,
                daily_water_goal: currentUser.daily_water_goal,
            });
        }
    }, [currentUser]);

    const updateMutation = useMutation({
        mutationFn: () => api.updateUserGoals(goals),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["user"] });
            queryClient.invalidateQueries({ queryKey: ["nutrition-summary"] });
            webApp?.HapticFeedback?.notificationOccurred("success");
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate();
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Settings</h1>

            {/* Profile */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Profile</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center gap-4">
                        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-xl">
                            {user?.first_name?.[0] || "👤"}
                        </div>
                        <div>
                            <div className="font-medium">
                                {user?.first_name} {user?.last_name}
                            </div>
                            {user?.username && (
                                <div className="text-sm text-muted-foreground">
                                    @{user.username}
                                </div>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Daily Goals */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Daily Goals</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <Label htmlFor="calories">Calorie Goal</Label>
                            <Input
                                id="calories"
                                type="number"
                                value={goals.daily_calorie_goal}
                                onChange={(e) =>
                                    setGoals({ ...goals, daily_calorie_goal: parseInt(e.target.value) || 0 })
                                }
                            />
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <Label htmlFor="protein">Protein (g)</Label>
                                <Input
                                    id="protein"
                                    type="number"
                                    value={goals.daily_protein_goal}
                                    onChange={(e) =>
                                        setGoals({ ...goals, daily_protein_goal: parseInt(e.target.value) || 0 })
                                    }
                                />
                            </div>
                            <div>
                                <Label htmlFor="carbs">Carbs (g)</Label>
                                <Input
                                    id="carbs"
                                    type="number"
                                    value={goals.daily_carbs_goal}
                                    onChange={(e) =>
                                        setGoals({ ...goals, daily_carbs_goal: parseInt(e.target.value) || 0 })
                                    }
                                />
                            </div>
                            <div>
                                <Label htmlFor="fat">Fat (g)</Label>
                                <Input
                                    id="fat"
                                    type="number"
                                    value={goals.daily_fat_goal}
                                    onChange={(e) =>
                                        setGoals({ ...goals, daily_fat_goal: parseInt(e.target.value) || 0 })
                                    }
                                />
                            </div>
                        </div>

                        <div>
                            <Label htmlFor="water">Water Goal (glasses)</Label>
                            <Input
                                id="water"
                                type="number"
                                value={goals.daily_water_goal}
                                onChange={(e) =>
                                    setGoals({ ...goals, daily_water_goal: parseInt(e.target.value) || 0 })
                                }
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                1 glass = 250ml
                            </p>
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            disabled={updateMutation.isPending}
                        >
                            {updateMutation.isPending ? "Saving..." : "Save Goals"}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            {/* App Info */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">About</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                    <p>Lifeguard v0.1.0</p>
                    <p>Your personal fitness & nutrition companion.</p>
                </CardContent>
            </Card>
        </div>
    );
}
