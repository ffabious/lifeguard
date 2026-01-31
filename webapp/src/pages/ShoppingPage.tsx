import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Check, ShoppingCart } from "lucide-react";
import { api, ShoppingItem, ShoppingCategory } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

const categoryEmoji: Record<ShoppingCategory, string> = {
    produce: "🥬",
    dairy: "🥛",
    meat: "🥩",
    seafood: "🐟",
    bakery: "🍞",
    frozen: "🧊",
    pantry: "🥫",
    beverages: "🥤",
    snacks: "🍿",
    supplements: "💊",
    other: "📦",
};

const categoryLabel: Record<ShoppingCategory, string> = {
    produce: "Produce",
    dairy: "Dairy",
    meat: "Meat",
    seafood: "Seafood",
    bakery: "Bakery",
    frozen: "Frozen",
    pantry: "Pantry",
    beverages: "Beverages",
    snacks: "Snacks",
    supplements: "Supplements",
    other: "Other",
};

export default function ShoppingPage() {
    const queryClient = useQueryClient();
    const [newItem, setNewItem] = useState("");
    const [newCategory, setNewCategory] = useState<ShoppingCategory>("other");

    const { data: items, isLoading } = useQuery({
        queryKey: ["shopping"],
        queryFn: () => api.getShoppingItems(),
    });

    const createMutation = useMutation({
        mutationFn: () =>
            api.createShoppingItem({
                name: newItem,
                category: newCategory,
            }),
        onSuccess: () => {
            setNewItem("");
            queryClient.invalidateQueries({ queryKey: ["shopping"] });
        },
    });

    const toggleMutation = useMutation({
        mutationFn: (id: number) => api.toggleShoppingItem(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["shopping"] });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number) => api.deleteShoppingItem(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["shopping"] });
        },
    });

    const clearPurchasedMutation = useMutation({
        mutationFn: () => api.clearPurchasedItems(),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["shopping"] });
        },
    });

    const handleAddItem = (e: React.FormEvent) => {
        e.preventDefault();
        if (!newItem.trim()) return;
        createMutation.mutate();
    };

    const pendingItems = items?.filter((item) => !item.is_purchased) || [];
    const purchasedItems = items?.filter((item) => item.is_purchased) || [];

    // Group items by category
    const itemsByCategory = pendingItems.reduce((acc, item) => {
        if (!acc[item.category]) {
            acc[item.category] = [];
        }
        acc[item.category].push(item);
        return acc;
    }, {} as Record<ShoppingCategory, ShoppingItem[]>);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Shopping List</h1>
                {purchasedItems.length > 0 && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => clearPurchasedMutation.mutate()}
                    >
                        Clear Purchased
                    </Button>
                )}
            </div>

            {/* Add Item Form */}
            <form onSubmit={handleAddItem} className="flex gap-2">
                <Input
                    value={newItem}
                    onChange={(e) => setNewItem(e.target.value)}
                    placeholder="Add item..."
                    className="flex-1"
                />
                <Select
                    value={newCategory}
                    onValueChange={(v) => setNewCategory(v as ShoppingCategory)}
                >
                    <SelectTrigger className="w-[130px]">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        {Object.entries(categoryLabel).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                                {categoryEmoji[value as ShoppingCategory]} {label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                <Button type="submit" disabled={!newItem.trim() || createMutation.isPending}>
                    <Plus className="h-4 w-4" />
                </Button>
            </form>

            {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : pendingItems.length === 0 && purchasedItems.length === 0 ? (
                <Card>
                    <CardContent className="py-8 text-center text-muted-foreground">
                        <ShoppingCart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Your shopping list is empty.</p>
                        <p className="text-sm">Add items above to get started!</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-6">
                    {/* Pending Items by Category */}
                    {Object.entries(itemsByCategory).map(([category, categoryItems]) => (
                        <div key={category}>
                            <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                                <span>{categoryEmoji[category as ShoppingCategory]}</span>
                                {categoryLabel[category as ShoppingCategory]}
                            </h3>
                            <div className="space-y-2">
                                {categoryItems.map((item) => (
                                    <ShoppingItemCard
                                        key={item.id}
                                        item={item}
                                        onToggle={() => toggleMutation.mutate(item.id)}
                                        onDelete={() => deleteMutation.mutate(item.id)}
                                    />
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Purchased Items */}
                    {purchasedItems.length > 0 && (
                        <div>
                            <h3 className="text-sm font-medium text-muted-foreground mb-2">
                                ✓ Purchased ({purchasedItems.length})
                            </h3>
                            <div className="space-y-2">
                                {purchasedItems.map((item) => (
                                    <ShoppingItemCard
                                        key={item.id}
                                        item={item}
                                        onToggle={() => toggleMutation.mutate(item.id)}
                                        onDelete={() => deleteMutation.mutate(item.id)}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function ShoppingItemCard({
    item,
    onToggle,
    onDelete,
}: {
    item: ShoppingItem;
    onToggle: () => void;
    onDelete: () => void;
}) {
    return (
        <Card className={cn(item.is_purchased && "opacity-60")}>
            <CardContent className="p-3">
                <div className="flex items-center gap-3">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onToggle}
                        className={cn(
                            "h-6 w-6 rounded-full border-2",
                            item.is_purchased
                                ? "bg-primary border-primary text-primary-foreground"
                                : "border-muted-foreground"
                        )}
                    >
                        {item.is_purchased && <Check className="h-3 w-3" />}
                    </Button>

                    <div className="flex-1">
                        <span
                            className={cn(
                                "font-medium",
                                item.is_purchased && "line-through text-muted-foreground"
                            )}
                        >
                            {item.name}
                        </span>
                        {item.quantity && (
                            <span className="text-sm text-muted-foreground ml-2">
                                ({item.quantity})
                            </span>
                        )}
                    </div>

                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onDelete}
                        className="text-muted-foreground hover:text-destructive h-8 w-8"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
