let list = document.getElementById("list");
let spotlight = document.getElementById("spotlight");
let templates = document.getElementById("templates");

let upcomingTemplate = templates.querySelector("li");

class Meeting {
    constructor(object) {
        this.start = new Date(object.start);
        this.duration = object.duration;
        this.title = object.stage.title;
        this.host = object.stage.host;
    }

    get end() {
        let date = new Date(this.start)
        date.setSeconds(date.getSeconds() + this.duration);
        return date;
    }
}

async function fetchSchedule() {
    const response = await fetch("./schedule.json", {
        method: "GET",
        cache: "no-cache"
    });

    return response.json()
        .then(data => data
            .map(item => new Meeting(item)));
}

/**
 * 
 * @param {Meeting[]} schedule 
 */
function updateView(schedule) {
    let now = new Date();

    let listElement = list.querySelector("ul");
    listElement.innerHTML = "";

    let upcoming = schedule
        .filter(meeting => meeting.end > now);
    if (upcoming.length == 0) {
        return;
    }

    if (upcoming[0].start < now) {
        let meeting = upcoming[0];
        upcoming = upcoming.slice(1, 9);
        document.body.dataset.spotlight = "yes";

        let startTime = meeting.start.getHours() + ":" + ("0" + meeting.start.getMinutes()).slice(-2);
        let endTime = meeting.end.getHours() + ":" + ("0" + meeting.end.getMinutes()).slice(-2);
        spotlight.querySelector(".timespan").innerText = startTime + " - " + endTime;
        spotlight.querySelector(".title").innerText = meeting.title;
        spotlight.querySelector(".host").innerText = meeting.host;

        let progress = 100 * (now.getTime() - meeting.start.getTime()) / (meeting.duration * 1000);
        spotlight.querySelector(".progress").style.width = progress + "%";
    } else {
        upcoming = upcoming.slice(0, 8);
        document.body.dataset.spotlight = "no";
    }

    upcoming.forEach(meeting => {
        let item = upcomingTemplate.cloneNode(true);
        item.querySelector(".time").innerText = meeting.start.getHours() + ":" + ("0" + meeting.start.getMinutes()).slice(-2);
        item.querySelector(".title").innerText = meeting.title;
        item.querySelector(".host").innerText = meeting.host;
        listElement.appendChild(item);

        let title = item.querySelector(".title");
        if (title.offsetWidth < title.scrollWidth) {
            title.innerHTML = "";

            var marquee = document.createElement("marquee");
            marquee.innerText = meeting.title;
            title.appendChild(marquee);
        }
    });
}

fetchSchedule().then(updateView)
window.setInterval(() => fetchSchedule().then(updateView), 60000);
