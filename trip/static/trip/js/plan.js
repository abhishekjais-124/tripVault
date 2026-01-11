(() => {
    const currencySymbol = (window.plannerBootstrap && window.plannerBootstrap.currencySymbol) || 'Rs ';
    const defaults = (window.plannerBootstrap && window.plannerBootstrap.defaults) || {};
    const tierMultipliers = { budget: 0.85, standard: 1, luxury: 1.25 };
    const initialMode = defaults.mode || 'group';

    const els = {
        dayCards: document.getElementById('day-cards'),
        addDay: document.getElementById('add-day'),
        duplicateDay: document.getElementById('duplicate-day'),
        peopleSlider: document.getElementById('people-slider'),
        peoplePill: document.getElementById('people-pill'),
        vehicleType: document.getElementById('vehicle-type'),
        vehicleCar: document.getElementById('vehicle-car'),
        vehicleTrain: document.getElementById('vehicle-train'),
        vehicleFlight: document.getElementById('vehicle-flight'),
        vehicleBike: document.getElementById('vehicle-bike'),
        tripFields: document.querySelectorAll('[data-trip-field]'),
        defaultMode: document.getElementById('default-mode'),
        tierToggle: document.getElementById('tier-toggle'),
        autoDays: document.getElementById('auto-days'),
        autoNights: document.getElementById('auto-nights'),
        resetPlanner: document.getElementById('reset-planner'),
        metricTrip: document.getElementById('metric-trip-total'),
        metricPerson: document.getElementById('metric-per-person'),
        metricDaily: document.getElementById('metric-daily-avg'),
        metricMode: document.getElementById('metric-trip-mode'),
        metricPeople: document.getElementById('metric-people-count'),
        metricDays: document.getElementById('metric-day-count'),
        categoryTotals: {
            stay: document.getElementById('total-stay'),
            transport: document.getElementById('total-transport'),
            food: document.getElementById('total-food'),
            activities: document.getElementById('total-activities'),
            misc: document.getElementById('total-misc'),
        },
        summary: {
            trip: document.getElementById('summary-trip-total'),
            person: document.getElementById('summary-per-person'),
            daily: document.getElementById('summary-daily-avg'),
            people: document.getElementById('summary-people'),
            days: document.getElementById('summary-days'),
            mode: document.getElementById('summary-mode'),
        },
        progress: {
            stay: document.getElementById('bar-stay'),
            transport: document.getElementById('bar-transport'),
            food: document.getElementById('bar-food'),
            activities: document.getElementById('bar-activities'),
            misc: document.getElementById('bar-misc'),
        },
        pct: {
            stay: document.getElementById('pct-stay'),
            transport: document.getElementById('pct-transport'),
            food: document.getElementById('pct-food'),
            activities: document.getElementById('pct-activities'),
            misc: document.getElementById('pct-misc'),
        },
        categoryChart: document.getElementById('category-chart'),
        save: document.getElementById('save-trip'),
        saveAsNewCheckbox: document.getElementById('save-as-new'),
        exportPdf: document.getElementById('export-pdf'),
        addCustomGlobal: document.getElementById('add-custom-global'),
        calcNote: document.getElementById('calculation-note'),
    };

    const state = {
        trip: {
            name: '',
            startDate: '',
            endDate: '',
            startCity: '',
            endCity: '',
            approxDistance: 0,
            vehicle: defaults.vehicle || 'car',
            mileage: defaults.mileage || 18,
            fuelPrice: defaults.fuelPrice || 105,
            bikeMileage: defaults.bikeMileage || 50,
            bikeFuelPrice: defaults.bikeFuelPrice || 100,
            trainTicket: defaults.trainTicket || 0,
            flightTicket: defaults.flightTicket || 0,
            people: defaults.people || 2,
            defaultMode: initialMode,
            tier: defaults.tier || 'standard',
        },
        days: [],
        globalCustom: [],
        lastSaved: null,
    };

    let pieChart = null;
    const prevNumbers = {};

    function debounce(fn, wait = 120) {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(null, args), wait);
        };
    }

    function uid(prefix = 'id') {
        return `${prefix}-${Math.random().toString(36).slice(2, 8)}-${Date.now()}`;
    }

    function numberify(value) {
        const n = parseFloat(value);
        return Number.isFinite(n) ? n : 0;
    }

    function formatCurrency(value) {
        const clean = Number.isFinite(value) ? value : 0;
        return `${currencySymbol}${clean.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    }

    function animateNumber(el, value) {
        if (!el) return;
        const target = Number.isFinite(value) ? value : 0;
        const start = prevNumbers[el.id] ?? 0;
        const startTime = performance.now();
        const duration = 360;
        function tick(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = start + (target - start) * (1 - Math.pow(1 - progress, 3));
            el.textContent = formatCurrency(eased);
            if (progress < 1) requestAnimationFrame(tick);
        }
        prevNumbers[el.id] = target;
        requestAnimationFrame(tick);
    }

    function currentMode() {
        return (state && state.trip && state.trip.defaultMode) || initialMode;
    }

    function createDay(seq, modeOverride) {
        const mode = modeOverride || currentMode();
        return {
            id: uid('day'),
            title: `Day ${seq}`,
            locations: '',
            importantPlans: '',
            distance: 0,
            transportMode: 'self',
            cabCost: 0,
            stay: { name: '', cost: 0 },
            food: {
                breakfast: { amount: 0, mode },
                lunch: { amount: 0, mode },
                dinner: { amount: 0, mode },
            },
            activities: [createActivity('Activity', mode)],
            misc: { parking: 0, toll: 0, snacks: 0, buffer: 0 },
            customExpenses: [],
            collapsed: false,
            panels: { stay: false, food: false, activities: false, misc: false },
        };
    }

    function createActivity(label = 'Activity', modeOverride) {
        return { id: uid('act'), name: label, cost: 0, mode: modeOverride || currentMode() };
    }

    function createCustomLine(label = 'Custom', modeOverride) {
        return { id: uid('custom'), name: label, cost: 0, mode: modeOverride || currentMode() };
    }

    function calcDay(day) {
        const people = Math.max(numberify(state.trip.people), 1);
        const distance = numberify(day.distance);
        const vehicle = state.trip.vehicle;

        let transportCost = 0;
        if (day.transportMode === 'cab') {
            transportCost = numberify(day.cabCost);
        } else {
            const fuelPrice = numberify(state.trip.fuelPrice);
            if (vehicle === 'car') {
                const mileage = Math.max(numberify(state.trip.mileage), 0.1);
                transportCost = (distance / mileage) * fuelPrice;
            } else if (vehicle === 'bike') {
                const mileage = Math.max(numberify(state.trip.bikeMileage), 0.1);
                transportCost = (distance / mileage) * fuelPrice;
            } else if (vehicle === 'train') {
                transportCost = numberify(state.trip.trainTicket) * people;
            } else if (vehicle === 'flight') {
                transportCost = numberify(state.trip.flightTicket) * people;
            }
        }

        const stay = numberify(day.stay && day.stay.cost);

        const food = day.food || {};
        const foodTotal = ['breakfast', 'lunch', 'dinner'].reduce((acc, key) => {
            const item = food[key] || { amount: 0, mode: currentMode() };
            const amt = numberify(item.amount);
            return acc + (item.mode === 'per-person' ? amt * people : amt);
        }, 0);

        const activities = Array.isArray(day.activities) ? day.activities : [];
        const activityTotal = activities.reduce((acc, act) => {
            const amt = numberify(act.cost);
            return acc + (act.mode === 'per-person' ? amt * people : amt);
        }, 0);

        const misc = day.misc || {};
        const miscList = numberify(misc.parking) + numberify(misc.toll) + numberify(misc.snacks) + numberify(misc.buffer);

        const customExpenses = Array.isArray(day.customExpenses) ? day.customExpenses : [];
        const customTotal = customExpenses.reduce((acc, line) => {
            const amt = numberify(line.cost);
            return acc + (line.mode === 'per-person' ? amt * people : amt);
        }, 0);

        const miscTotal = miscList + customTotal;
        const categories = { stay, transport: transportCost, food: foodTotal, activities: activityTotal, misc: miscTotal };
        const dayTotal = Object.values(categories).reduce((a, b) => a + b, 0);

        return { categories, dayTotal, fuel: transportCost };
    }

    function aggregate() {
        const multiplier = tierMultipliers[state.trip.tier] ?? 1;
        const computedDays = state.days.map((day) => ({ ...day, totals: calcDay(day) }));

        const baseTotals = computedDays.reduce(
            (acc, item) => {
                acc.stay += item.totals.categories.stay;
                acc.transport += item.totals.categories.transport;
                acc.food += item.totals.categories.food;
                acc.activities += item.totals.categories.activities;
                acc.misc += item.totals.categories.misc;
                acc.baseTrip += item.totals.dayTotal;
                acc.fuel += item.totals.fuel;
                return acc;
            },
            { stay: 0, transport: 0, food: 0, activities: 0, misc: 0, baseTrip: 0, fuel: 0 }
        );

        const adjustedCategories = {
            stay: baseTotals.stay * multiplier,
            transport: baseTotals.transport * multiplier,
            food: baseTotals.food * multiplier,
            activities: baseTotals.activities * multiplier,
            misc: baseTotals.misc * multiplier,
        };

        const adjustedTrip = baseTotals.baseTrip * multiplier;
        const people = Math.max(numberify(state.trip.people), 1);

        const globalCustom = state.globalCustom.reduce((acc, line) => {
            const amt = numberify(line.cost);
            return acc + (line.mode === 'per-person' ? amt * people : amt);
        }, 0);

        const totalWithGlobal = adjustedTrip + globalCustom;

        return {
            computedDays,
            categories: adjustedCategories,
            tripTotal: totalWithGlobal,
            perPerson: totalWithGlobal / people,
            dailyAvg: totalWithGlobal / Math.max(state.days.length, 1),
            multiplier,
            globalCustom,
            baseTotals,
        };
    }

    const render = debounce(() => {
        const data = aggregate();
        renderHero(data);
        renderDays(data);
        renderCategories(data);
        renderSummary(data);
        renderChart(data);
        persistDraft();
    }, 80);

    const renderDebounced = debounce(() => {
        const data = aggregate();
        renderHero(data);
        renderCategories(data);
        renderSummary(data);
        renderChart(data);
        persistDraft();
    }, 300);

    function renderHero(data) {
        animateNumber(els.metricTrip, data.tripTotal);
        animateNumber(els.metricPerson, data.perPerson);
        animateNumber(els.metricDaily, data.dailyAvg);
        if (els.metricMode) els.metricMode.textContent = `${capitalize(state.trip.tier)} mode`;
        if (els.metricPeople) els.metricPeople.textContent = `${state.trip.people} people`;
        if (els.metricDays) els.metricDays.textContent = `${state.days.length} days`;
        if (els.autoDays) els.autoDays.textContent = autoDaysFromDates();
        if (els.autoNights) els.autoNights.textContent = autoDaysFromDates() > 0 ? autoDaysFromDates() - 1 : 0;
    }

    function renderCategories(data) {
        Object.entries(els.categoryTotals).forEach(([key, el]) => {
            animateNumber(el, data.categories[key]);
        });
    }

    function renderSummary(data) {
        animateNumber(els.summary.trip, data.tripTotal);
        animateNumber(els.summary.person, data.perPerson);
        animateNumber(els.summary.daily, data.dailyAvg);
        if (els.summary.people) els.summary.people.textContent = state.trip.people;
        if (els.summary.days) els.summary.days.textContent = state.days.length;
        if (els.summary.mode) els.summary.mode.textContent = capitalize(state.trip.tier);

        const total = data.tripTotal || 1;
        const pct = {
            stay: Math.round((data.categories.stay / total) * 100),
            transport: Math.round((data.categories.transport / total) * 100),
            food: Math.round((data.categories.food / total) * 100),
            activities: Math.round((data.categories.activities / total) * 100),
            misc: Math.round((data.categories.misc / total) * 100),
        };

        ['stay', 'transport', 'food', 'activities', 'misc'].forEach((key) => {
            if (els.progress[key]) els.progress[key].style.width = `${pct[key]}%`;
            if (els.pct[key]) els.pct[key].textContent = `${pct[key]}%`;
        });
    }

    function renderChart(data) {
        if (!els.categoryChart || !window.Chart) return;
        const labels = ['Stay', 'Transport', 'Food', 'Activities', 'Misc'];
        const values = [
            data.categories.stay,
            data.categories.transport,
            data.categories.food,
            data.categories.activities,
            data.categories.misc,
        ];
        if (!pieChart) {
            pieChart = new Chart(els.categoryChart.getContext('2d'), {
                type: 'pie',
                data: {
                    labels,
                    datasets: [
                        {
                            data: values,
                            backgroundColor: ['#22d3ee', '#3b82f6', '#a855f7', '#f97316', '#e11d48'],
                            borderWidth: 0,
                        },
                    ],
                },
                options: {
                    plugins: { legend: { labels: { color: '#e5e7eb' } } },
                },
            });
        } else {
            pieChart.data.datasets[0].data = values;
            pieChart.update();
        }
    }

    function renderDays(data) {
        els.dayCards.innerHTML = data.computedDays
            .map((day, index) => buildDayCard(day, index, data.multiplier))
            .join('');
    }

    function buildDayCard(day, index, multiplier) {
        const totalAdjusted = day.totals.dayTotal * multiplier;
        const fuel = day.totals.categories.transport * multiplier;
        const activities = Array.isArray(day.activities) ? day.activities : [];
        const misc = day.misc || {};
        const stay = day.stay || { name: '', cost: 0 };
        const customExpenses = Array.isArray(day.customExpenses) ? day.customExpenses : [];
        const foodObj = day.food || {};

        const panels = day.panels || { stay: false, food: false, activities: false, misc: false };

        const activityRows = activities
            .map(
                (act) => `
                <div class="table-row" data-activity-id="${act.id}">
                    <input class="field-input" type="text" value="${escapeHtml(act.name)}" placeholder="Activity" data-action="edit-activity" data-field="name">
                    <input class="field-input" type="number" min="0" step="0.01" value="${act.cost}" data-action="edit-activity" data-field="cost">
                    <div class="cost-toggle">
                        <button type="button" class="${act.mode === 'group' ? 'active' : ''}" data-action="set-activity-mode" data-mode="group">Group</button>
                        <button type="button" class="${act.mode === 'per-person' ? 'active' : ''}" data-action="set-activity-mode" data-mode="per-person">Per person</button>
                    </div>
                    <button type="button" class="remove-btn" data-action="remove-activity"><i class="fas fa-times"></i></button>
                </div>`
            )
            .join('');

        const customRows = customExpenses
            .map(
                (line) => `
                <div class="table-row" data-custom-id="${line.id}">
                    <input class="field-input" type="text" value="${escapeHtml(line.name)}" placeholder="Label" data-action="edit-custom" data-field="name">
                    <input class="field-input" type="number" min="0" step="0.01" value="${line.cost}" data-action="edit-custom" data-field="cost">
                    <div class="cost-toggle">
                        <button type="button" class="${line.mode === 'group' ? 'active' : ''}" data-action="set-custom-mode" data-mode="group">Group</button>
                        <button type="button" class="${line.mode === 'per-person' ? 'active' : ''}" data-action="set-custom-mode" data-mode="per-person">Per person</button>
                    </div>
                    <button type="button" class="remove-btn" data-action="remove-custom"><i class="fas fa-times"></i></button>
                </div>`
            )
            .join('');

        const collapsedClass = day.collapsed ? 'collapsed' : '';
        const panelClass = (key) => (panels[key] ? 'panel-open' : 'panel-closed');
        const panelToggle = (key, label) => `
            <div class="panel-header" data-action="toggle-panel" data-panel="${key}" style="pointer-events: auto;">
                <div style="flex: 1; display: flex; align-items: center; gap: 8px;"><i class="fas fa-plus-circle"></i> <span>${label}</span></div>
                <span style="color: var(--muted); font-size: 13px; font-weight: 600;">${panels[key] ? 'Hide' : 'Add'}</span>
            </div>`;

        return `
        <div class="day-card ${collapsedClass}" data-day-id="${day.id}" draggable="true">
            <div class="day-header">
                <input class="field-input day-title-input" type="text" value="${escapeHtml(day.title)}" data-day-field="title">
                <div class="day-actions">
                    <span class="drag-handle" title="Drag to reorder"><i class="fas fa-grip-vertical"></i></span>
                    <button class="ghost-btn" type="button" data-action="duplicate-day"><i class="fas fa-clone"></i></button>
                    <button class="ghost-btn" type="button" data-action="collapse-day"><i class="fas fa-chevron-${day.collapsed ? 'down' : 'up'}"></i></button>
                    <button class="remove-btn" type="button" data-action="remove-day"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            <div class="day-body">
                <div>
                    <label class="field-label">Locations</label>
                    <textarea class="field-textarea" data-day-field="locations" placeholder="Ex: Bangalore → Gokarna">${escapeHtml(day.locations)}</textarea>
                </div>

                <div class="mt-4">
                    <label class="field-label">Important plans</label>
                    <textarea class="field-textarea" data-day-field="importantPlans" placeholder="Ex: Sunset hike, Museum visit, Dinner reservation">${escapeHtml(day.importantPlans)}</textarea>
                </div>

                <div class="transport-grid mt-4">
                    <div>
                        <label class="field-label">Transport</label>
                        <div class="toggle-group" data-day-id="${day.id}">
                            <button type="button" class="toggle ${day.transportMode === 'self' ? 'active' : ''}" data-action="transport-mode" data-mode="self">Self</button>
                            <button type="button" class="toggle ${day.transportMode === 'cab' ? 'active' : ''}" data-action="transport-mode" data-mode="cab">Cab</button>
                        </div>
                        <p class="info-pill mt-2 ${day.transportMode === 'self' ? '' : 'hidden'}">Fuel: ${formatCurrency(fuel)} · Mileage: ${state.trip.mileage} km/l</p>
                    </div>
                    <div class="${day.transportMode === 'self' ? '' : 'hidden'}">
                        <label class="field-label">Distance (km)</label>
                        <input class="field-input" type="number" min="0" step="0.1" value="${day.distance}" data-day-field="distance">
                    </div>
                    <div class="${day.transportMode === 'cab' ? '' : 'hidden'}">
                        <label class="field-label">Cab total (group)</label>
                        <input class="field-input" type="number" min="0" step="0.01" value="${day.cabCost || 0}" data-day-field="cabCost" placeholder="Cab cost">
                    </div>
                </div>

                <div class="panel ${panelClass('stay')}">
                    ${panelToggle('stay', 'Stay')}
                    <div class="panel-body">
                        <input class="field-input" type="text" placeholder="Hotel / stay" value="${escapeHtml(stay.name)}" data-day-field="stay.name">
                        <input class="field-input mt-2" type="number" min="0" step="0.01" value="${stay.cost || 0}" data-day-field="stay.cost" placeholder="Total stay cost">
                    </div>
                </div>

                <div class="panel ${panelClass('food')}">
                    ${panelToggle('food', 'Food (Breakfast, Lunch, Dinner)')}
                    <div class="panel-body">
                        ${['breakfast','lunch','dinner'].map((key) => foodRow(foodObj, key)).join('')}
                    </div>
                </div>

                <div class="panel ${panelClass('activities')}">
                    ${panelToggle('activities', 'Activities')}
                    <div class="panel-body">
                        <div class="table-like">${activityRows || '<div class="table-row"><p class="badge-soft">No activities yet</p></div>'}</div>
                        <button class="add-line mt-2" type="button" data-action="add-activity"><i class="fas fa-plus"></i> Add activity</button>
                    </div>
                </div>

                <div class="panel ${panelClass('misc')}">
                    ${panelToggle('misc', 'Misc + Custom')}
                    <div class="panel-body">
                        <div class="subgrid two">
                            ${miscRow('Parking', 'parking', misc.parking || 0)}
                            ${miscRow('Toll', 'toll', misc.toll || 0)}
                            ${miscRow('Snacks', 'snacks', misc.snacks || 0)}
                            ${miscRow('Emergency buffer', 'buffer', misc.buffer || 0)}
                        </div>
                        <div class="table-like mt-3">${customRows}</div>
                        <button class="add-line mt-2" type="button" data-action="add-custom"><i class="fas fa-plus"></i> Custom expense</button>
                    </div>
                </div>

                <div class="card-footer">
                    <div class="badge-soft">Day ${index + 1}</div>
                    <div class="day-total">Day total: ${formatCurrency(totalAdjusted)}</div>
                </div>
            </div>
        </div>`;
    }

    function foodRow(foodObj, key) {
        const item = (foodObj && foodObj[key]) || { amount: 0, mode: currentMode() };
        const label = key.charAt(0).toUpperCase() + key.slice(1);
        return `
        <div class="food-row mt-2">
            <label class="field-label">${label}</label>
            <div class="food-input-group">
                <input class="field-input" type="number" min="0" step="0.01" value="${item.amount}" data-day-field="food.${key}.amount" placeholder="${label} cost">
                <div class="cost-toggle">
                    <button type="button" class="${item.mode === 'group' ? 'active' : ''}" data-action="set-food-mode" data-key="${key}" data-mode="group">Group</button>
                    <button type="button" class="${item.mode === 'per-person' ? 'active' : ''}" data-action="set-food-mode" data-key="${key}" data-mode="per-person">Per person</button>
                </div>
            </div>
        </div>`;
    }

    function miscRow(label, key, value) {
        return `
        <div>
            <label class="field-label">${label}</label>
            <input class="field-input" type="number" min="0" step="0.01" value="${value}" data-day-field="misc.${key}">
        </div>`;
    }

    function escapeHtml(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function setDayValue(dayId, path, value) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        const parts = path.split('.');
        let ref = day;
        parts.forEach((key, idx) => {
            if (idx === parts.length - 1) {
                ref[key] = key === 'amount' || key === 'cost' || key === 'distance' ? numberify(value) : value;
            } else {
                ref[key] = ref[key] || {};
                ref = ref[key];
            }
        });
    }

    function addDay(copyLast = false) {
        const base = copyLast && state.days.length ? deepCopy(state.days[state.days.length - 1]) : createDay(state.days.length + 1);
        base.id = uid('day');
        state.days.push(base);
        render();
    }

    function duplicateDay(dayId) {
        const original = state.days.find((d) => d.id === dayId);
        if (!original) return;
        const clone = deepCopy(original);
        clone.id = uid('day');
        clone.title = `${original.title} copy`;
        clone.activities = clone.activities.map((a) => ({ ...a, id: uid('act') }));
        clone.customExpenses = clone.customExpenses.map((c) => ({ ...c, id: uid('custom') }));
        state.days.splice(state.days.indexOf(original) + 1, 0, clone);
        render();
    }

    function removeDay(dayId) {
        if (state.days.length === 1) return;
        state.days = state.days.filter((d) => d.id !== dayId);
        render();
    }

    function toggleCollapse(dayId) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.collapsed = !day.collapsed;
        render();
    }

    function togglePanel(dayId, panelKey) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.panels = day.panels || { stay: false, food: false, activities: false, misc: false };
        day.panels[panelKey] = !day.panels[panelKey];
        render();
    }

    function addActivity(dayId) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.activities.push(createActivity('New activity'));
        render();
    }

    function removeActivity(dayId, actId) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.activities = day.activities.filter((a) => a.id !== actId);
        render();
    }

    function updateActivity(dayId, actId, field, value) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        const act = day.activities.find((a) => a.id === actId);
        if (!act) return;
        if (field === 'cost') act.cost = numberify(value);
        else act[field] = value;
        render();
    }

    function addCustom(dayId) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.customExpenses.push(createCustomLine('Custom item'));
        render();
    }

    function removeCustom(dayId, customId) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        day.customExpenses = day.customExpenses.filter((c) => c.id !== customId);
        render();
    }

    function updateCustom(dayId, customId, field, value) {
        const day = state.days.find((d) => d.id === dayId);
        if (!day) return;
        const line = day.customExpenses.find((c) => c.id === customId);
        if (!line) return;
        if (field === 'cost') line.cost = numberify(value);
        else line[field] = value;
        render();
    }

    function deepCopy(obj) {
        return typeof structuredClone === 'function' ? structuredClone(obj) : JSON.parse(JSON.stringify(obj));
    }

    function capitalize(str) {
        return String(str || '').charAt(0).toUpperCase() + String(str || '').slice(1);
    }

    function autoDaysFromDates() {
        if (!state.trip.startDate || !state.trip.endDate) return 0;
        const start = new Date(state.trip.startDate);
        const end = new Date(state.trip.endDate);
        const diff = (end - start) / (1000 * 60 * 60 * 24);
        return diff >= 0 ? Math.floor(diff) + 1 : 0;
    }

    function handleTripInput(e) {
        const field = e.target.dataset.tripField;
        if (!field) return;
        let value = e.target.value;
        if (['people', 'mileage', 'fuelPrice', 'bikeMileage', 'bikeFuelPrice', 'trainTicket', 'flightTicket', 'approxDistance'].includes(field)) {
            value = numberify(value);
        }
        state.trip[field] = value;
        if (field === 'people') syncPeopleInputs(value);
        if (field === 'vehicle') updateVehicleVisibility();
        render();
    }

    function syncPeopleInputs(value) {
        if (els.peoplePill) els.peoplePill.textContent = value;
        if (els.peopleSlider) els.peopleSlider.value = value;
    }

    function updateVehicleVisibility() {
        const vehicle = state.trip.vehicle;
        [els.vehicleCar, els.vehicleTrain, els.vehicleFlight, els.vehicleBike].forEach(el => {
            if (el) el.style.display = 'none';
        });
        if (vehicle === 'car' && els.vehicleCar) els.vehicleCar.style.display = 'block';
        if (vehicle === 'train' && els.vehicleTrain) els.vehicleTrain.style.display = 'block';
        if (vehicle === 'flight' && els.vehicleFlight) els.vehicleFlight.style.display = 'block';
        if (vehicle === 'bike' && els.vehicleBike) els.vehicleBike.style.display = 'block';
    }

    function bindTripSetup() {
        els.tripFields.forEach((input) => input.addEventListener('input', handleTripInput));
        if (els.peopleSlider)
            els.peopleSlider.addEventListener('input', (e) => {
                const val = numberify(e.target.value);
                state.trip.people = Math.max(1, val);
                syncPeopleInputs(state.trip.people);
                render();
            });

        if (els.defaultMode)
            els.defaultMode.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-mode]');
                if (!btn) return;
                state.trip.defaultMode = btn.dataset.mode;
                els.defaultMode.querySelectorAll('button').forEach((b) => b.classList.toggle('active', b === btn));
                render();
            });

        if (els.tierToggle)
            els.tierToggle.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-tier]');
                if (!btn) return;
                state.trip.tier = btn.dataset.tier;
                els.tierToggle.querySelectorAll('button').forEach((b) => b.classList.toggle('active', b === btn));
                render();
            });

        if (els.resetPlanner)
            els.resetPlanner.addEventListener('click', () => {
                if (!confirm('Reset all days and itineraries? Trip setup will remain.')) return;
                
                // Only reset days and global custom expenses
                state.days = [createDay(1, state.trip.defaultMode)];
                state.globalCustom = [];
                
                // Update localStorage
                persistDraft();
                render();
            });
    }

    function bindGlobalButtons() {
        if (els.addDay) els.addDay.addEventListener('click', () => addDay(false));
        if (els.duplicateDay) els.duplicateDay.addEventListener('click', () => addDay(true));
        if (els.addCustomGlobal)
            els.addCustomGlobal.addEventListener('click', () => {
                if (!state.days.length) return;
                addCustom(state.days[state.days.length - 1].id);
            });
        if (els.save) els.save.addEventListener('click', saveTrip);
        if (els.exportPdf) els.exportPdf.addEventListener('click', () => window.print());
    }

    function bindDayEvents() {
        els.dayCards.addEventListener('input', (e) => {
            const card = e.target.closest('.day-card');
            if (!card) return;
            const dayId = card.dataset.dayId;
            const dayField = e.target.dataset.dayField;
            if (dayField) {
                setDayValue(dayId, dayField, e.target.value);
                renderDebounced();
                return;
            }
            const action = e.target.dataset.action;
            if (action === 'edit-activity') {
                const row = e.target.closest('[data-activity-id]');
                if (!row) return;
                updateActivity(dayId, row.dataset.activityId, e.target.dataset.field, e.target.value);
                renderDebounced();
                return;
            }
            if (action === 'edit-custom') {
                const row = e.target.closest('[data-custom-id]');
                if (!row) return;
                updateCustom(dayId, row.dataset.customId, e.target.dataset.field, e.target.value);
                renderDebounced();
                return;
            }
        });

        els.dayCards.addEventListener('click', (e) => {
            const card = e.target.closest('.day-card');
            if (!card) return;
            const dayId = card.dataset.dayId;

            // Check for panel-header (div with data-action)
            const panelHeader = e.target.closest('[data-action="toggle-panel"]');
            if (panelHeader) {
                const panel = panelHeader.dataset.panel;
                if (panel) togglePanel(dayId, panel);
                return;
            }

            // Check for button actions
            const btn = e.target.closest('button');
            if (!btn) return;
            const action = btn.dataset.action;

            if (action === 'collapse-day') return toggleCollapse(dayId);
            if (action === 'remove-day') return removeDay(dayId);
            if (action === 'duplicate-day') return duplicateDay(dayId);
            if (action === 'add-activity') return addActivity(dayId);
            if (action === 'remove-activity') {
                const row = e.target.closest('[data-activity-id]');
                if (row) removeActivity(dayId, row.dataset.activityId);
                return;
            }
            if (action === 'set-activity-mode') {
                const row = e.target.closest('[data-activity-id]');
                if (row) updateActivity(dayId, row.dataset.activityId, 'mode', btn.dataset.mode);
                return;
            }
            if (action === 'set-food-mode') {
                const key = btn.dataset.key;
                if (key) {
                    const day = state.days.find((d) => d.id === dayId);
                    if (day) day.food[key].mode = btn.dataset.mode;
                    render();
                }
                return;
            }
            if (action === 'add-custom') return addCustom(dayId);
            if (action === 'remove-custom') {
                const row = e.target.closest('[data-custom-id]');
                if (row) removeCustom(dayId, row.dataset.customId);
                return;
            }
            if (action === 'set-custom-mode') {
                const row = e.target.closest('[data-custom-id]');
                if (row) updateCustom(dayId, row.dataset.customId, 'mode', btn.dataset.mode);
                return;
            }
            if (action === 'transport-mode') {
                const mode = btn.dataset.mode;
                const day = state.days.find((d) => d.id === dayId);
                if (day && mode) {
                    day.transportMode = mode;
                    render();
                }
                return;
            }
        });

        // Drag & drop reorder
        let dragEl = null;
        els.dayCards.addEventListener('dragstart', (e) => {
            dragEl = e.target.closest('.day-card');
            if (!dragEl) return;
            dragEl.classList.add('dragging');
        });

        els.dayCards.addEventListener('dragend', () => {
            if (dragEl) dragEl.classList.remove('dragging');
            const newOrder = Array.from(els.dayCards.children).map((c) => c.dataset.dayId);
            state.days.sort((a, b) => newOrder.indexOf(a.id) - newOrder.indexOf(b.id));
            render();
            dragEl = null;
        });

        els.dayCards.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(els.dayCards, e.clientY);
            const dragging = els.dayCards.querySelector('.dragging');
            if (!dragging) return;
            if (afterElement == null) {
                els.dayCards.appendChild(dragging);
            } else {
                els.dayCards.insertBefore(dragging, afterElement);
            }
        });
    }

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.day-card:not(.dragging)')];
        return draggableElements.reduce(
            (closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset, element: child };
                }
                return closest;
            },
            { offset: Number.NEGATIVE_INFINITY, element: null }
        ).element;
    }

    function saveDraftNotice() {
        persistDraft();
        if (els.calcNote) {
            els.calcNote.textContent = 'Draft saved locally.';
            setTimeout(() => (els.calcNote.textContent = 'All numbers update live.'), 2400);
        }
    }

    function persistDraft() {
        try {
            const payload = JSON.stringify(state);
            localStorage.setItem('trip-planner-draft', payload);
            // Mark when draft was last saved
            localStorage.setItem('trip-planner-draft-time', new Date().toISOString());
        } catch (err) {
            console.warn('Unable to persist draft', err);
        }
    }

    let saveAsNew = false;  // Flag to force creating a new trip on next save

    // Auto-save every 5 seconds as a safety net
    setInterval(() => {
        if (state.days && state.days.length > 0) {
            persistDraft();
        }
    }, 5000);

    function saveTrip() {
        const tripName = state.trip.name || 'Untitled Trip';
        let tripId = localStorage.getItem('current-trip-id');
        
        // Check if "Save as new trip" checkbox is checked
        const saveAsNew = els.saveAsNewCheckbox && els.saveAsNewCheckbox.checked;
        
        if (saveAsNew) {
            tripId = null;  // Force create new trip
            // Optionally add " (copy)" to name if not already there
            if (!state.trip.name.includes('(copy)')) {
                state.trip.name = state.trip.name + ' (copy)';
                const tripNameInput = document.getElementById('trip-name');
                if (tripNameInput) tripNameInput.value = state.trip.name;
            }
        }
        
        const payload = {
            id: tripId ? parseInt(tripId) : null,
            trip: state.trip,
            days: state.days,
            globalCustom: state.globalCustom
        };
        
        fetch('/home/api/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (res.status === 401) {
                alert('Please log in to save trips.');
                window.location.href = '/user/login/';
                return null;
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.success) {
                localStorage.setItem('current-trip-id', data.trip_id);
                
                // Uncheck the "save as new" checkbox after successful save
                if (els.saveAsNewCheckbox) {
                    els.saveAsNewCheckbox.checked = false;
                }
                
                // Check if this was a new trip
                const wasNewTrip = saveAsNew;
                
                if (els.calcNote) {
                    els.calcNote.innerHTML = data.message + (wasNewTrip ? ' <a href="/home/saved/" style="color: #22d3ee; text-decoration: underline; margin-left: 10px;">View all trips →</a>' : '');
                    setTimeout(() => (els.calcNote.textContent = 'All numbers update live.'), 4000);
                } else {
                    alert(data.message);
                }
            } else {
                alert('Error: ' + (data.message || 'Failed to save trip'));
                console.error('Save trip error:', data);
            }
        })
        .catch(err => {
            console.error('Error saving trip:', err);
            alert('Failed to save trip. ' + err.message);
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function loadDraft() {
        try {
            const saved = localStorage.getItem('trip-planner-draft');
            if (!saved) return;
            const data = JSON.parse(saved);
            Object.assign(state.trip, data.trip || {});
            state.days = data.days || state.days;
            state.globalCustom = data.globalCustom || [];
            syncPeopleInputs(state.trip.people || 1);
            syncFormInputsWithState();
        } catch (err) {
            console.warn('No saved draft', err);
        }
    }

    function syncFormInputsWithState() {
        // Sync trip setup inputs with current state
        if (document.getElementById('trip-name')) document.getElementById('trip-name').value = state.trip.name || '';
        if (document.getElementById('start-date')) document.getElementById('start-date').value = state.trip.startDate || '';
        if (document.getElementById('end-date')) document.getElementById('end-date').value = state.trip.endDate || '';
        if (document.getElementById('start-city')) document.getElementById('start-city').value = state.trip.startCity || '';
        if (document.getElementById('end-city')) document.getElementById('end-city').value = state.trip.endCity || '';
        if (document.getElementById('approx-distance')) document.getElementById('approx-distance').value = state.trip.approxDistance || 0;
        if (document.getElementById('vehicle-type')) document.getElementById('vehicle-type').value = state.trip.vehicle || 'car';
        if (document.getElementById('mileage')) document.getElementById('mileage').value = state.trip.mileage || 18;
        if (document.getElementById('fuel-price')) document.getElementById('fuel-price').value = state.trip.fuelPrice || 105;
        if (document.getElementById('bike-mileage')) document.getElementById('bike-mileage').value = state.trip.bikeMileage || 50;
        if (document.getElementById('bike-fuel-price')) document.getElementById('bike-fuel-price').value = state.trip.bikeFuelPrice || 100;
        if (document.getElementById('train-ticket')) document.getElementById('train-ticket').value = state.trip.trainTicket || 0;
        if (document.getElementById('flight-ticket')) document.getElementById('flight-ticket').value = state.trip.flightTicket || 0;
        if (document.getElementById('people-slider')) {
            document.getElementById('people-slider').value = state.trip.people || 2;
            syncPeopleInputs(state.trip.people || 2);
        }
        if (document.getElementById('tier-toggle')) document.getElementById('tier-toggle').value = state.trip.tier || 'standard';
        if (document.getElementById('default-mode')) document.getElementById('default-mode').value = state.trip.defaultMode || 'group';
        updateVehicleVisibility();
        // Trigger a full render to show all days and expenses
        render();
    }

    function shareLink() {
        try {
            const encoded = btoa(JSON.stringify(state));
            const url = `${window.location.origin}${window.location.pathname}?plan=${encodeURIComponent(encoded)}`;
            navigator.clipboard.writeText(url);
            if (els.calcNote) {
                els.calcNote.textContent = 'Shareable link copied';
                setTimeout(() => (els.calcNote.textContent = 'All numbers update live.'), 2400);
            }
        } catch (err) {
            console.warn('Share link failed', err);
        }
    }

    function hydrateFromQuery() {
        const params = new URLSearchParams(window.location.search);
        if (!params.has('plan')) return;
        try {
            const decoded = JSON.parse(atob(params.get('plan')));
            Object.assign(state.trip, decoded.trip || {});
            state.days = decoded.days || state.days;
            state.globalCustom = decoded.globalCustom || [];
        } catch (err) {
            console.warn('Failed to hydrate from link', err);
        }
    }

    function init() {
        loadDraft();
        hydrateFromQuery();
        if (!state.days.length) state.days = [createDay(1, state.trip.defaultMode)];
        bindTripSetup();
        bindGlobalButtons();
        bindDayEvents();
        syncPeopleInputs(state.trip.people);
        updateVehicleVisibility();
        render();
    }

    document.addEventListener('DOMContentLoaded', init);
})();
