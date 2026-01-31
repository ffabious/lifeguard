import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { api, MealType } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

const mealTypes: { value: MealType; label: string }[] = [
    { value: "breakfast", label: "🌅 Breakfast" },
    { value: "lunch", label: "☀️ Lunch" },
    { value: "dinner", label: "🌙 Dinner" },
    { value: "snack", label: "🍎 Snack" },
];

export default function NewMealPage() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [name, setName] = useState("");
    const [mealType, setMealType] = useState<MealType>("lunch");
    const [calories, setCalories] = useState("");
    const [protein, setProtein] = useState("");
    const [carbs, setCarbs] = useState("");
    const [fat, setFat] = useState("");
    const [servingSize, setServingSize] = useState("");
    const [notes, setNotes] = useState("");

    const createMutation = useMutation({
        mutationFn: () =>
            api.createMeal({
                name,
                meal_type: mealType,
                calories: calories ? parseInt(calories) : undefined,
                protein: protein ? parseFloat(protein) : undefined,
                carbs: carbs ? parseFloat(carbs) : undefined,
                fat: fat ? parseFloat(fat) : undefined,
                serving_size: servingSize || undefined,
                notes: notes || undefined,
                meal_date: format(new Date(), "yyyy-MM-dd"),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["meals"] });
            queryClient.invalidateQueries({ queryKey: ["nutrition-summary"] });
            navigate("/nutrition");
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        createMutation.mutate();
    };

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Log Meal</h1>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <Label htmlFor="name">What did you eat?</Label>
                    <Input
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Grilled chicken salad, etc."
                        required
                    />
                </div>

                <div>
                    <Label htmlFor="type">Meal Type</Label>
                    <Select value={mealType} onValueChange={(v) => setMealType(v as MealType)}>
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {mealTypes.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                    {type.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div>
                    <Label htmlFor="serving">Serving Size</Label>
                    <Input
                        id="serving"
                        value={servingSize}
                        onChange={(e) => setServingSize(e.target.value)}
                        placeholder="1 plate, 200g, etc."
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label htmlFor="calories">Calories</Label>
                        <Input
                            id="calories"
                            type="number"
                            value={calories}
                            onChange={(e) => setCalories(e.target.value)}
                            placeholder="400"
                        />
                    </div>
                    <div>
                        <Label htmlFor="protein">Protein (g)</Label>
                        <Input
                            id="protein"
                            type="number"
                            value={protein}
                            onChange={(e) => setProtein(e.target.value)}
                            placeholder="30"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <Label htmlFor="carbs">Carbs (g)</Label>
                        <Input
                            id="carbs"
                            type="number"
                            value={carbs}
                            onChange={(e) => setCarbs(e.target.value)}
                            placeholder="50"
                        />
                    </div>
                    <div>
                        <Label htmlFor="fat">Fat (g)</Label>
                        <Input
                            id="fat"
                            type="number"
                            value={fat}
                            onChange={(e) => setFat(e.target.value)}
                            placeholder="15"
                        />
                    </div>
                </div>

                <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Input
                        id="notes"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Any notes about this meal"
                    />
                </div>

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
                        {createMutation.isPending ? "Saving..." : "Save Meal"}
                    </Button>
                </div>
            </form>
        </div>
    );
}
