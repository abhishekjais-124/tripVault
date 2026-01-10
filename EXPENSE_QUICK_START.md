# Expense Feature - Quick Start Guide

## 🚀 Getting Started

### 1. **Access Expenses**
- Navigate to your Groups page
- Each group card now has a **green "Expenses"** button
- Click it to view group expenses

### 2. **Add Your First Expense**
- Click **"Add Expense"** button (top right)
- Fill in the form:
  - **Title**: What was it for? (e.g., "Restaurant Dinner")
  - **Amount**: How much was paid? (e.g., 2250)
  - **Date**: When? (defaults to today)
  - **Category**: What type? (Food, Transport, etc.)
  - **Description**: Any notes? (optional)
- Select **"Equal Split"** (divides equally among all members)
- Click **"Add Expense"**

### 3. **View Expenses**
After adding, you'll see:
- **Your Balance** at the top (green if you're owed, red if you owe)
- **Table of all expenses** with:
  - When it was
  - What it was for
  - Who paid
  - How much it was
  - Your share in the expense
  - Whether you paid or owe

### 4. **Delete an Expense**
- Only you can delete expenses you created
- Click the **trash icon** next to your expense
- Confirm the deletion

---

## 📊 Understanding Your Balance

### Balance Display
At the top of the expenses page, you'll see:

```
YOUR BALANCE: ₹500
You are owed money
```

**Color Coding:**
- 🟢 **Green**: You are owed money (creditor)
- 🔴 **Red**: You owe money (debtor)

### Example Scenario
**Group with 3 people spending ₹2250 on dinner:**

| Person | Amount | Your Balance | Status |
|--------|--------|--------------|--------|
| You    | +₹2250 | +₹750        | Owed money |
| Person B | -₹750 | | Owes you |
| Person C | -₹750 | | Owes you |

You paid ₹2250, others owe you ₹750 each = **Balance: +₹750 owed to you**

---

## 🎨 Expense Categories

Choose the category that best fits:

| Category | Icon | Color | Use For |
|----------|------|-------|---------|
| Food | 🍽️ | Orange | Meals, restaurants |
| Transport | 🚗 | Purple | Flights, taxis, gas |
| Accommodation | 🏨 | Pink | Hotels, stays |
| Activity | 🎉 | Indigo | Tours, entertainment |
| Shopping | 🛍️ | Rose | Souvenirs, gifts |
| Utilities | ⚡ | Slate | Tickets, subscriptions |
| Other | 📝 | Gray | Everything else |

---

## 📋 Table Columns Explained

| Column | What It Shows |
|--------|--------------|
| **Date** | When the expense happened (MM/DD) |
| **Title** | What the expense was for |
| **Category** | Type (color-coded) |
| **Paid By** | Who paid (with profile pic) |
| **Amount Paid** | Total amount paid |
| **Your Share** | What portion is yours (green if you paid, red if you owe) |
| **Status** | "You Paid" or "You Owe" indicator |
| **Action** | Delete button (only if you created it) |

---

## 💡 Tips & Tricks

### Equal vs Custom Split

**Equal Split** (Default)
- Automatically divides amount by number of members
- Best for: Group dinners, shared hotel rooms
- Example: ₹3000 ÷ 3 people = ₹1000 each

**Custom Split**
- You specify exact amount for each person
- Best for: Someone had extra items, specific amounts
- Example: ₹3000 split as ₹1500, ₹1000, ₹500

### Sorting
- **Always sorted by date** (newest first)
- Makes it easy to find recent expenses
- Month/year shown for clarity

### Quick Balance Check
- **Top card shows your overall balance** with the group
- See if you owe or are owed at a glance
- Green = good (you're getting money back)
- Red = you need to pay

---

## ⚠️ Important Notes

### Permissions
- ✅ You can **delete expenses you created**
- ❌ You cannot **delete expenses others created**
- ✅ You can **delete your own expense** anytime

### Calculations
- Balances are **automatically calculated**
- Equal split is calculated when you add the expense
- No manual settlement tracking yet (coming soon!)

### Categories
- Help organize expenses
- Filtered view coming in future updates
- No impact on balance calculations

---

## 🔧 Troubleshooting

### "Expenses" button not showing?
- Make sure you're a member of the group
- Refresh the page
- Clear browser cache

### Balance not updating?
- Refresh the page (Cmd+R or Ctrl+R)
- Check that all group members are active
- Verify the expense was added successfully

### Can't delete an expense?
- You can only delete expenses you created
- Someone else created this expense
- Ask them to delete it if needed

### Confused about your balance?
- Green (+) = you're owed money
- Red (-) = you owe money
- Check the table for individual breakdowns

---

## 📱 UI Elements

### Buttons

**Green Button** 📊
- Label: "Expenses"
- Location: Group card header
- Purpose: View all group expenses

**Blue "Add Expense" Button** ➕
- Location: Top right of expenses page
- Purpose: Add new expense
- Returns to: Same page after adding

**White "Add Expense" Button** (Form)
- Location: Bottom of add expense form
- Purpose: Submit the form
- Action: Creates expense and shows updated list

**Cancel Link** ❌
- Location: Bottom of form
- Purpose: Go back without saving
- Returns to: Expenses list

**Trash Icon** 🗑️
- Location: Each expense row (your expenses only)
- Purpose: Delete that specific expense
- Confirmation: Browser will ask "Delete this expense?"

---

## 🎯 Common Use Cases

### Case 1: Group Dinner
```
1. One person pays for everyone: ₹2250
2. Click "Add Expense"
3. Title: "Restaurant Dinner"
4. Amount: 2250
5. Category: "Food"
6. Equal Split (auto-divides 3 ways)
→ Each person owes ₹750
```

### Case 2: Hotel Room Split
```
1. Hotel cost: ₹5000 for 2 nights
2. Click "Add Expense"
3. Title: "Hotel Stay 2 nights"
4. Amount: 5000
5. Category: "Accommodation"
6. Equal Split (3 people = ₹1666.67 each)
→ Everyone owes the same amount
```

### Case 3: Checking Who Owes What
```
1. Click "Expenses" on group
2. Look at top card "YOUR BALANCE"
3. If Red ₹500: You owe the group ₹500
4. Check table for details
5. Person A: you owe ₹250
   Person B: you owe ₹250
```

---

## 📞 Need Help?

### Check Documentation
- See `EXPENSE_FEATURE.md` for complete docs
- Check app structure in project overview

### Verify Setup
- Admin panel: http://localhost:8000/admin/
- Check Expense models are listed
- View expenses in Django admin

---

## ✅ Quick Checklist

- [ ] Navigate to a group
- [ ] See green "Expenses" button
- [ ] Click it
- [ ] See expenses page with balance
- [ ] Click "Add Expense"
- [ ] Fill in form with test data
- [ ] Select "Equal Split"
- [ ] Submit
- [ ] See new expense in list
- [ ] Check balance updated
- [ ] Try deleting own expense

**All working?** 🎉 **Feature is ready to use!**

---

## 🚀 Ready to Track Expenses!

The expense feature is fully integrated and ready. Start tracking group expenses and balances now!

For detailed information, see the full documentation: `EXPENSE_FEATURE.md`
