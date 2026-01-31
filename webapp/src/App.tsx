import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useTelegram } from "@/hooks/useTelegram";
import Layout from "@/components/Layout";
import HomePage from "@/pages/HomePage";
import WorkoutsPage from "@/pages/WorkoutsPage";
import NewWorkoutPage from "@/pages/NewWorkoutPage";
import NutritionPage from "@/pages/NutritionPage";
import NewMealPage from "@/pages/NewMealPage";
import ShoppingPage from "@/pages/ShoppingPage";
import SettingsPage from "@/pages/SettingsPage";

function App() {
    const { isReady } = useTelegram();

    if (!isReady) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<HomePage />} />
                    <Route path="workouts" element={<WorkoutsPage />} />
                    <Route path="workout/new" element={<NewWorkoutPage />} />
                    <Route path="nutrition" element={<NutritionPage />} />
                    <Route path="nutrition/new" element={<NewMealPage />} />
                    <Route path="shopping" element={<ShoppingPage />} />
                    <Route path="settings" element={<SettingsPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
