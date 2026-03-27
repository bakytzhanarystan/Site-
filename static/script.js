const taskList = document.getElementById("taskList")
const totalTasksEl = document.getElementById("totalTasks")
const completedTasksEl = document.getElementById("completedTasks")
const percentCompletedEl = document.getElementById("percentCompleted")
const progressFill = document.getElementById("progress")

const aiResultEl = document.getElementById("aiResult")

// загрузка при открытии страницы
window.onload = () => {
    loadTasks()
}


// ---------- ЗАГРУЗКА ЗАДАЧ ----------

async function loadTasks(filter = "all") {

    const res = await fetch("/tasks")
    const tasks = await res.json()

    taskList.innerHTML = ""

    let completed = 0

    tasks.forEach(task => {

        if(filter === "completed" && !task.completed) return
        if(filter === "active" && task.completed) return

        const li = document.createElement("li")

        if(task.completed) {
            li.classList.add("completed")
            completed++
        }

        li.innerHTML = `
            <div>
                <b>${task.text}</b><br>
                Дедлайн: ${task.deadline || "-"} |
                Приоритет: ${task.priority || "-"}
            </div>

            <div>
                <button class="task-btn" onclick="toggleComplete(${task.id}, ${task.completed})">
                    ${task.completed ? "Отменить" : "Выполнено"}
                </button>

                <button class="task-btn" onclick="deleteTask(${task.id})">
                    Удалить
                </button>
            </div>
        `

        taskList.appendChild(li)

    })

    updateStats(tasks.length, completed)
}



// ---------- ДОБАВЛЕНИЕ ----------

async function addTask() {

    const text = document.getElementById("taskInput").value
    const deadline = document.getElementById("deadlineInput").value
    const priority = document.getElementById("priorityInput").value

    if(!text){
        alert("Введите задачу")
        return
    }

    const res = await fetch("/add_task",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            text,
            deadline,
            priority
        })
    })

    const data = await res.json()

    if(data.status === "ok"){

        document.getElementById("taskInput").value = ""
        document.getElementById("deadlineInput").value = ""

        loadTasks()
    }
}



// ---------- УДАЛЕНИЕ ----------

async function deleteTask(id){

    await fetch(`/delete_task/${id}`,{
        method:"DELETE"
    })

    loadTasks()
}



// ---------- ВЫПОЛНЕНО ----------

async function toggleComplete(id, completed){

    await fetch(`/toggle_complete/${id}`,{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            completed: !completed
        })
    })

    loadTasks()
}



// ---------- СТАТИСТИКА ----------

function updateStats(total, completed){

    totalTasksEl.innerText = "Всего задач: " + total
    completedTasksEl.innerText = "Выполнено: " + completed

    const percent = total ? Math.round(completed / total * 100) : 0

    percentCompletedEl.innerText = "Прогресс: " + percent + "%"

    progressFill.style.width = percent + "%"
}



// ---------- AI ----------

async function askAI(){
    aiResultEl.innerText = "AI думает..."

    const res = await fetch("/ai", {
        method: "POST"
    })

    const data = await res.json()

    aiResultEl.innerText = data.recommendation.replace(/\*+/g, "").trim()
}



// ---------- ФИЛЬТР ----------

function filterTasks(type){
    loadTasks(type)
}

// ---------- СОВЕТЫ ----------

const tips = [
"Разделите большую задачу на несколько маленьких.",
"Начните день с самой важной задачи.",
"Работайте 25 минут и делайте короткий перерыв.",
"Уберите телефон во время выполнения задач.",
"Планируйте задачи на день утром.",
"Закрывайте одну задачу полностью перед следующей.",
"Начинайте с задач с ближайшим дедлайном.",
"Записывайте все задачи, чтобы ничего не забыть.",
"Ставьте реальные сроки выполнения.",
"Делайте сложные задачи, пока уровень энергии высокий.",
"Не откладывайте маленькие задачи — делайте их сразу.",
"Работайте в тихом месте без отвлекающих факторов.",
"Делайте перерыв каждые 1–2 часа работы.",
"Используйте таймер, чтобы контролировать время.",
"Начинайте работу с самой сложной задачи.",
"Ставьте конкретные цели на день.",
"Не перегружайте себя слишком большим количеством задач.",
"Следите за дедлайнами заранее.",
"Разбивайте учебу на короткие сессии.",
"Держите рабочее место в порядке.",
"Планируйте задачи на неделю вперед.",
"Убирайте отвлекающие сайты во время работы.",
"Начинайте выполнять задачи сразу, не откладывая.",
"Отмечайте выполненные задачи — это мотивирует.",
"Работайте в одно и то же время каждый день.",
"Используйте список задач для контроля дел.",
"Сначала делайте важные задачи, потом мелкие.",
"Не пытайтесь делать несколько дел одновременно.",
"Фокусируйтесь на одной задаче.",
"Не бойтесь делегировать задачи, если это возможно.",
"Проверяйте прогресс в конце дня.",
"Разбивайте большие проекты на этапы.",
"Планируйте отдых так же, как и работу.",
"Используйте календарь для дедлайнов.",
"Записывайте идеи сразу, чтобы не забыть.",
"Начинайте подготовку к экзаменам заранее.",
"Не ждите идеального момента для начала.",
"Сначала выполняйте задачи с высоким приоритетом.",
"Старайтесь завершать задачи в тот же день.",
"Создайте утренний ритуал начала работы.",
"Следите за балансом работы и отдыха.",
"Проверяйте список задач утром и вечером.",
"Старайтесь выполнять хотя бы одну важную задачу в день.",
"Минимизируйте отвлекающие уведомления.",
"Работайте короткими, но продуктивными сессиями.",
"Развивайте привычку планировать.",
"Старайтесь выполнять задачи раньше дедлайна.",
"Не бойтесь корректировать план.",
"Учитесь говорить 'нет' лишним задачам.",
"Главное — начать, дальше будет легче."
];

let lastTipIndex = -1;

function newTip(){

    let random;

    // чтобы совет не повторялся
    do{
        random = Math.floor(Math.random() * tips.length);
    } while(random === lastTipIndex);

    lastTipIndex = random;

    const tipText = document.getElementById("tipText");

    // плавное исчезновение
    tipText.style.opacity = 0;

    setTimeout(() => {

        tipText.innerText = tips[random];

        // плавное появление
        tipText.style.opacity = 1;

    }, 300);
}