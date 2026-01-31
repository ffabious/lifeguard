import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Link } from "react-router-dom";
import { Plus, Trash2, Clock, Flame } from "lucide-react";
import { api, Workout, WorkoutType } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const workoutTypeEmoji: Record<WorkoutType, string> = {
    strength: "💪",
    cardio: "🏃",
    flexibility: "🧘",
    hiit: "⚡",
    sports: "⚽",
    other: "🏋️",
};

const workoutTypeLabel: Record<WorkoutType, string> = {
    strength: "Strength",
    cardio: "Cardio",
    flexibility: "Flexibility",
    hiit: "HIIT",
    sports: "Sports",
    other: "Other",
};

export default function WorkoutsPage() {
    const queryClient = useQueryClient();

    const { data: workouts, isLoading } = useQuery({
        queryKey: ["workouts"],
        queryFn: () => api.getWorkouts(),
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number) => api.deleteWorkout(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["workouts"] });
        },
    });

    const handleDelete = (id: number) => {
        if (confirm("Are you sure you want to delete this workout?")) {
            deleteMutation.mutate(id);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Workouts</h1>
                <Button asChild>
                    <Link to="/workout/new">
                        <Plus className="h-4 w-4 mr-2" />
                        New
                    </Link>
                </Button>
            </div>

            {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : workouts?.length === 0 ? (
                <Card>
                    <CardContent className="py-8 text-center text-muted-foreground">
                        <p>No workouts yet.</p>
                        <p className="text-sm">Start tracking your fitness journey!</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-3">
                    {workouts?.map((workout) => (
                        <WorkoutCard
                            key={workout.id}
                            workout={workout}
                            onDelete={() => handleDelete(workout.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function WorkoutCard({
    workout,
    onDelete,
}: {
    workout: Workout;
    onDelete: () => void;
}) {
    return (
        <Card>
            <CardContent className="p-4">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">
                                {workoutTypeEmoji[workout.workout_type]}
                            </span>
                            <div>
                                <h3 className="font-semibold">{workout.name}</h3>
                                <p className="text-sm text-muted-foreground">
                                    {workoutTypeLabel[workout.workout_type]} •{" "}
                                    {format(new Date(workout.workout_date), "MMM d, yyyy")}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {workout.duration_minutes} min
                            </div>
                            {workout.calories_burned && (
                                <div className="flex items-center gap-1">
                                    <Flame className="h-3 w-3" />
                                    {workout.calories_burned} cal
                                </div>
                            )}
                            {workout.exercises.length > 0 && (
                                <span>{workout.exercises.length} exercises</span>
                            )}
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
