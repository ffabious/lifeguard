import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Link } from "react-router-dom";
import { Plus, Trash2, Droplets } from "lucide-react";
import { api, Meal, MealType } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const mealTypeEmoji: Record<MealType, string> = {
    breakfast: "🌅",
    lunch: "☀️",
    dinner: "🌙",
    snack: "🍎",
};

const mealTypeLabel: Record<MealType, string> = {
    breakfast: "Breakfast",
    lunch: "Lunch",
    dinner: "Dinner",
    snack: "Snack",
};

export default function NutritionPage() {
    const queryClient = useQueryClient();
    const today = format(new Date(), "yyyy-MM-dd");

    const { data: meals, isLoading } = useQuery({
        queryKey: ["meals", today],
        queryFn: () => api.getMeals(today),
    });

    const { data: summary } = useQuery({
        queryKey: ["nutrition-summary", today],
        queryFn: () => api.getDailyNutritionSummary(today),
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number) => api.deleteMeal(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["meals"] });
            queryClient.invalidateQueries({ queryKey: ["nutrition-summary"] });
        },
    });

    const waterMutation = useMutation({
        mutationFn: () => api.logWater(1),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["nutrition-summary"] });
        },
    });

    const handleDelete = (id: number) => {
        if (confirm("Are you sure you want to delete this meal?")) {
            deleteMutation.mutate(id);
        }
    };

    // Group meals by type
    const mealsByType = meals?.reduce((acc, meal) => {
        if (!acc[meal.meal_type]) {
            acc[meal.meal_type] = [];
        }
        acc[meal.meal_type].push(meal);
        return acc;
    }, {} as Record<MealType, Meal[]>);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Nutrition</h1>
                <Button asChild>
                    <Link to="/nutrition/new">
                        <Plus className="h-4 w-4 mr-2" />
                        Log Meal
                    </Link>
                </Button>
            </div>

            {/* Daily Summary */}
            {summary && (
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">Today's Progress</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span>Calories</span>
                                <span>
                                    {summary.total_calories} / {summary.calorie_goal}
                                </span>
                            </div>
                            <Progress value={summary.calorie_progress} className="h-2" />
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <div className="text-sm text-muted-foreground">Protein</div>
                                <div className="font-medium">{summary.total_protein}g</div>
                                <Progress value={summary.protein_progress} className="h-1 mt-1" />
                            </div>
                            <div>
                                <div className="text-sm text-muted-foreground">Carbs</div>
                                <div className="font-medium">{summary.total_carbs}g</div>
                                <Progress value={summary.carbs_progress} className="h-1 mt-1" />
                            </div>
                            <div>
                                <div className="text-sm text-muted-foreground">Fat</div>
                                <div className="font-medium">{summary.total_fat}g</div>
                                <Progress value={summary.fat_progress} className="h-1 mt-1" />
                            </div>
                        </div>

                        {/* Water */}
                        <div className="flex items-center justify-between pt-2 border-t">
                            <div className="flex items-center gap-2">
                                <Droplets className="h-4 w-4 text-blue-500" />
                                <span>
                                    {summary.water_glasses} / {summary.water_goal} glasses
                                </span>
                            </div>
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={() => waterMutation.mutate()}
                                disabled={waterMutation.isPending}
                            >
                                <Plus className="h-3 w-3 mr-1" />
                                Add Water
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Meals by Type */}
            {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : meals?.length === 0 ? (
                <Card>
                    <CardContent className="py-8 text-center text-muted-foreground">
                        <p>No meals logged today.</p>
                        <p className="text-sm">Start tracking what you eat!</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-4">
                    {(["breakfast", "lunch", "dinner", "snack"] as MealType[]).map(
                        (type) =>
                            mealsByType?.[type] && (
                                <div key={type}>
                                    <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                                        <span>{mealTypeEmoji[type]}</span>
                                        {mealTypeLabel[type]}
                                    </h3>
                                    <div className="space-y-2">
                                        {mealsByType[type].map((meal) => (
                                            <MealCard
                                                key={meal.id}
                                                meal={meal}
                                                onDelete={() => handleDelete(meal.id)}
                                            />
                                        ))}
                                    </div>
                                </div>
                            )
                    )}
                </div>
            )}
        </div>
    );
}

function MealCard({ meal, onDelete }: { meal: Meal; onDelete: () => void }) {
    return (
        <Card>
            <CardContent className="p-3">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="font-medium">{meal.name}</div>
                        <div className="text-sm text-muted-foreground">
                            {meal.calories && <span>{meal.calories} cal</span>}
                            {meal.protein && <span> • {meal.protein}g protein</span>}
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onDelete}
                        className="text-muted-foreground hover:text-destructive"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
