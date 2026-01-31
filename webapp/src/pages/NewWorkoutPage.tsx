import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Plus, X } from "lucide-react";
import { api, WorkoutType, ExerciseCreate } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

const workoutTypes: { value: WorkoutType; label: string }[] = [
    { value: "strength", label: "💪 Strength" },
    { value: "cardio", label: "🏃 Cardio" },
    { value: "flexibility", label: "🧘 Flexibility" },
    { value: "hiit", label: "⚡ HIIT" },
    { value: "sports", label: "⚽ Sports" },
    { value: "other", label: "🏋️ Other" },
];

export default function NewWorkoutPage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [name, setName] = useState("");
    const [workoutType, setWorkoutType] = useState<WorkoutType>("strength");
    const [duration, setDuration] = useState("");
    const [calories, setCalories] = useState("");
    const [notes, setNotes] = useState("");
    const [exercises, setExercises] = useState<ExerciseCreate[]>([]);

    const createMutation = useMutation({
        mutationFn: () =>
            api.createWorkout({
                name,
                workout_type: workoutType,
                duration_minutes: parseInt(duration) || 0,
                calories_burned: calories ? parseInt(calories) : undefined,
                notes: notes || undefined,
                workout_date: format(new Date(), "yyyy-MM-dd"),
                exercises,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["workouts"] });
            queryClient.invalidateQueries({ queryKey: ["workout-summary"] });
            navigate("/workouts");
        },
    });

    const addExercise = () => {
        setExercises([
            ...exercises,
            { name: "", sets: undefined, reps: undefined, weight: undefined, order: exercises.length },
        ]);
    };

    const updateExercise = (index: number, field: keyof ExerciseCreate, value: string | number | undefined) => {
        const updated = [...exercises];
        updated[index] = { ...updated[index], [field]: value };
        setExercises(updated);
    };

    const removeExercise = (index: number) => {
        setExercises(exercises.filter((_, i) => i !== index));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        createMutation.mutate();
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Log Workout</h1>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <Label htmlFor="name">Workout Name</Label>
                    <Input
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Morning Run, Leg Day, etc."
                        required
                    />
                </div>

                <div>
                    <Label htmlFor="type">Workout Type</Label>
                    <Select value={workoutType} onValueChange={(v) => setWorkoutType(v as WorkoutType)}>
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {workoutTypes.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                    {type.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label htmlFor="duration">Duration (min)</Label>
                        <Input
                            id="duration"
                            type="number"
                            value={duration}
                            onChange={(e) => setDuration(e.target.value)}
                            placeholder="30"
                        />
                    </div>
                    <div>
                        <Label htmlFor="calories">Calories Burned</Label>
                        <Input
                            id="calories"
                            type="number"
                            value={calories}
                            onChange={(e) => setCalories(e.target.value)}
                            placeholder="200"
                        />
                    </div>
                </div>

                <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Input
                        id="notes"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="How did it go?"
                    />
                </div>

                {/* Exercises */}
                <Card>
                    <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-base">Exercises</CardTitle>
                            <Button type="button" variant="outline" size="sm" onClick={addExercise}>
                                <Plus className="h-4 w-4 mr-1" />
                                Add
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {exercises.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-2">
                                No exercises added yet
                            </p>
                        ) : (
                            exercises.map((exercise, index) => (
                                <div key={index} className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                                    <div className="flex-1 space-y-2">
                                        <Input
                                            value={exercise.name}
                                            onChange={(e) => updateExercise(index, "name", e.target.value)}
                                            placeholder="Exercise name"
                                        />
                                        <div className="grid grid-cols-3 gap-2">
                                            <Input
                                                type="number"
                                                value={exercise.sets || ""}
                                                onChange={(e) => updateExercise(index, "sets", parseInt(e.target.value) || undefined)}
                                                placeholder="Sets"
                                            />
                                            <Input
                                                type="number"
                                                value={exercise.reps || ""}
                                                onChange={(e) => updateExercise(index, "reps", parseInt(e.target.value) || undefined)}
                                                placeholder="Reps"
                                            />
                                            <Input
                                                type="number"
                                                value={exercise.weight || ""}
                                                onChange={(e) => updateExercise(index, "weight", parseFloat(e.target.value) || undefined)}
                                                placeholder="Weight"
                                            />
                                        </div>
                                    </div>
                                    <Button
                                        type="button"
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => removeExercise(index)}
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                </div>
                            ))
                        )}
                    </CardContent>
                </Card>

                <div className="flex gap-3">
                    <Button
                        type="button"
                        variant="outline"
                        className="flex-1"
                        onClick={() => navigate(-1)}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        className="flex-1"
                        disabled={!name.trim() || createMutation.isPending}
                    >
                        {createMutation.isPending ? "Saving..." : "Save Workout"}
                    </Button>
                </div>
            </form>
        </div>
    );
}
