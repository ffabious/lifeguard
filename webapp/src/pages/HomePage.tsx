import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Link } from "react-router-dom";
import { Dumbbell, Apple, Droplets, Plus, ShoppingCart } from "lucide-react";
import { api } from "@/lib/api";
import { useTelegram } from "@/hooks/useTelegram";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

export default function HomePage() {
    const { user } = useTelegram();
    const today = format(new Date(), "yyyy-MM-dd");

    const { data: nutritionSummary } = useQuery({
        queryKey: ["nutrition-summary", today],
        queryFn: () => api.getDailyNutritionSummary(today),
    });

    const { data: workoutSummary } = useQuery({
        queryKey: ["workout-summary"],
        queryFn: () => api.getWeeklyWorkoutSummary(),
    });

    const { data: shoppingSummary } = useQuery({
        queryKey: ["shopping-summary"],
        queryFn: () => api.getShoppingSummary(),
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">
                    Hello, {user?.first_name || "there"}! 👋
                </h1>
                <p className="text-muted-foreground">
                    {format(new Date(), "EEEE, MMMM d")}
                </p>
            </div>

            {/* Quick actions */}
            <div className="grid grid-cols-2 gap-3">
                <Button asChild className="h-auto py-4 flex-col gap-2">
                    <Link to="/workout/new">
                        <Dumbbell className="h-5 w-5" />
                        <span>Log Workout</span>
                    </Link>
                </Button>
                <Button asChild variant="secondary" className="h-auto py-4 flex-col gap-2">
                    <Link to="/nutrition/new">
                        <Apple className="h-5 w-5" />
                        <span>Log Meal</span>
                    </Link>
                </Button>
            </div>

            {/* Today's Nutrition */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Apple className="h-5 w-5 text-green-500" />
                        Today's Nutrition
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {nutritionSummary ? (
                        <>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>Calories</span>
                                    <span>
                                        {nutritionSummary.total_calories} / {nutritionSummary.calorie_goal}
                                    </span>
                                </div>
                                <Progress value={nutritionSummary.calorie_progress} className="h-2" />
                            </div>

                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div>
                                    <div className="text-lg font-semibold">
                                        {nutritionSummary.total_protein}g
                                    </div>
                                    <div className="text-xs text-muted-foreground">Protein</div>
                                    <Progress
                                        value={nutritionSummary.protein_progress}
                                        className="h-1 mt-1"
                                    />
                                </div>
                                <div>
                                    <div className="text-lg font-semibold">
                                        {nutritionSummary.total_carbs}g
                                    </div>
                                    <div className="text-xs text-muted-foreground">Carbs</div>
                                    <Progress
                                        value={nutritionSummary.carbs_progress}
                                        className="h-1 mt-1"
                                    />
                                </div>
                                <div>
                                    <div className="text-lg font-semibold">
                                        {nutritionSummary.total_fat}g
                                    </div>
                                    <div className="text-xs text-muted-foreground">Fat</div>
                                    <Progress
                                        value={nutritionSummary.fat_progress}
                                        className="h-1 mt-1"
                                    />
                                </div>
                            </div>

                            {/* Water */}
                            <div className="flex items-center justify-between pt-2 border-t">
                                <div className="flex items-center gap-2">
                                    <Droplets className="h-4 w-4 text-blue-500" />
                                    <span className="text-sm">Water</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm">
                                        {nutritionSummary.water_glasses} / {nutritionSummary.water_goal} glasses
                                    </span>
                                    <WaterButton />
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-4 text-muted-foreground">
                            Loading...
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Weekly Workouts */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Dumbbell className="h-5 w-5 text-orange-500" />
                        This Week
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {workoutSummary ? (
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold">
                                    {workoutSummary.total_workouts}
                                </div>
                                <div className="text-xs text-muted-foreground">Workouts</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold">
                                    {workoutSummary.total_duration_minutes}
                                </div>
                                <div className="text-xs text-muted-foreground">Minutes</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold">
                                    {workoutSummary.total_calories_burned}
                                </div>
                                <div className="text-xs text-muted-foreground">Calories</div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-4 text-muted-foreground">
                            Loading...
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Shopping List */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <ShoppingCart className="h-5 w-5 text-purple-500" />
                            Shopping List
                        </div>
                        <Button asChild variant="ghost" size="sm">
                            <Link to="/shopping">View All</Link>
                        </Button>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {shoppingSummary ? (
                        <div className="text-sm">
                            <span className="font-medium">{shoppingSummary.pending_items}</span>{" "}
                            items to buy
                            {shoppingSummary.purchased_items > 0 && (
                                <span className="text-muted-foreground">
                                    {" "}• {shoppingSummary.purchased_items} purchased
                                </span>
                            )}
                        </div>
                    ) : (
                        <div className="text-muted-foreground">Loading...</div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function WaterButton() {
    const queryClient = useQueryClient();
    const { mutate: logWater, isPending } = useMutation({
        mutationFn: () => api.logWater(1),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["nutrition-summary"] });
        },
    });

    return (
        <Button
            size="sm"
            variant="outline"
            disabled={isPending}
            onClick={() => logWater()}
        >
            <Plus className="h-3 w-3" />
        </Button>
    );
}
