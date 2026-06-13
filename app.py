import streamlit as st

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="ChefTodo", page_icon="🍳", layout="centered")

# Mock Database for Recipes & Costs
RECIPE_DB = {
    "Breakfast": {
        "Avocado Toast": {"ingredients": {"Avocado": 1.50, "Bread": 0.50, "Eggs": 0.40}, "subs": {"Avocado": "Hummus"}},
        "Oatmeal Berry Bowl": {"ingredients": {"Oats": 0.30, "Milk": 0.50, "Berries": 2.00, "Honey": 0.20}, "subs": {"Milk": "Almond Milk", "Berries": "Banana"}},
        "Pancakes": {"ingredients": {"Flour": 0.20, "Milk": 0.40, "Eggs": 0.40, "Syrup": 0.50}, "subs": {"Eggs": "Applesauce"}}
    },
    "Lunch": {
        "Chicken Caesar Salad": {"ingredients": {"Chicken Breast": 3.00, "Romaine Lettuce": 1.00, "Caesar Dressing": 0.50, "Croutons": 0.30}, "subs": {"Chicken Breast": "Tofu"}},
        "Quinoa Salad Bowl": {"ingredients": {"Quinoa": 0.80, "Cucumber": 0.50, "Tomatoes": 0.60, "Feta Cheese": 1.20}, "subs": {"Feta Cheese": "Olives"}},
        "Tomato Basil Soup & Grilled Cheese": {"ingredients": {"Canned Tomatoes": 1.00, "Bread": 0.50, "Cheddar Cheese": 1.00, "Butter": 0.30}, "subs": {"Cheddar Cheese": "Vegan Cheese"}}
    },
    "Dinner": {
        "Salmon with Asparagus": {"ingredients": {"Salmon Fillet": 7.00, "Asparagus": 2.50, "Lemon": 0.50, "Olive Oil": 0.30}, "subs": {"Salmon Fillet": "Chicken Breast"}},
        "Garlic Mushroom Pasta": {"ingredients": {"Pasta": 0.50, "Mushrooms": 1.50, "Garlic": 0.20, "Heavy Cream": 1.00, "Parmesan": 0.80}, "subs": {"Heavy Cream": "Coconut Milk"}},
        "Lentil Coconut Curry": {"ingredients": {"Lentils": 0.60, "Coconut Milk": 1.20, "Curry Paste": 0.50, "Rice": 0.40, "Spinach": 0.80}, "subs": {"Spinach": "Kale"}}
    }
}

# --- APP UI & LOGIC ---
st.title("🍳 ChefTodo")
st.caption("A minimal, budget-conscious daily meal planner and to-do generator.")
st.markdown("---")

# Section 1: User Preferences & Budget
st.subheader("1. Setup Your Day")
col1, col2 = st.columns(2)

with col1:
    daily_budget = st.number_input("Daily Food Budget ($)", min_value=5.0, max_value=100.0, value=20.0, step=1.0)

with col2:
    dietary_note = st.text_input("Dietary Notes / Constraints (e.g., Vegetarian, No Dairy)", placeholder="Optional")

# Section 2: Meal Selection
st.subheader("2. Plan Your Meals")
selected_meals = {}
for meal_type in ["Breakfast", "Lunch", "Dinner"]:
    options = list(RECIPE_DB[meal_type].keys())
    selected_meals[meal_type] = st.selectbox(f"Select {meal_type}", options)

# Section 3: Processing Logistics
total_cost = 0.0
grocery_list = {}
substitution_guide = {}

for meal_type, recipe_name in selected_meals.items():
    recipe_data = RECIPE_DB[meal_type][recipe_name]
    
    # Accumulate Groceries & Costs
    for ing, price in recipe_data["ingredients"].items():
        grocery_list[ing] = grocery_list.get(ing, 0.0) + price
        total_cost += price
    
    # Accumulate Substitutions
    for ing, sub in recipe_data["subs"].items():
        substitution_guide[ing] = sub

st.markdown("---")

# Section 4: Budget Feasibility Logic Dashboard
st.subheader("3. Budget Feasibility Status")

if total_cost <= daily_budget:
    st.success(f"🟢 **Within Budget!** Total estimated cost is **${total_cost:.2f}** out of your **${daily_budget:.2f}** limit.")
else:
    st.error(f"🔴 **Budget Alert!** Total estimated cost is **${total_cost:.2f}**, which exceeds your **${daily_budget:.2f}** budget by **${(total_cost - daily_budget):.2f}**.")
    st.info("💡 *Tip: Consider swapping out premium items (like Salmon) to bring down costs.*")

# Section 5: The Generated Output (To-Do / Action Plan)
st.markdown("---")
st.subheader("📋 Your Personalized Cooking To-Do List")

tabs = st.tabs(["🍽️ Meal Schedule", "🛒 Grocery List", "🔄 Smart Substitutions"])

with tabs[0]:
    st.markdown("### Today's Menu")
    for meal_type, recipe in selected_meals.items():
        st.write(f"**{meal_type}:** {recipe}")

with tabs[1]:
    st.markdown("### Ingredients to Buy / Prep")
    st.caption("Check items off as you shop or cook:")
    for item, price in grocery_list.items():
        st.checkbox(f"{item} — (${price:.2f})", key=f"shop_{item}")

with tabs[2]:
    st.markdown("### Handy Substitutions")
    st.caption("Missing an ingredient? Try these alternatives instead:")
    if substitution_guide:
        for original, sub in substitution_guide.items():
            st.markdown(f"- Instead of **{original}**, you can use **{sub}**")
    else:
        st.write("No default substitutions needed for this selection.")