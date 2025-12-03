const form = document.getElementById('planForm');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const destinations = document.getElementById('destinations').value;
  const start_date = document.getElementById('start_date').value;
  const end_date = document.getElementById('end_date').value;
  const budget = document.getElementById('budget').value;
  const style = document.getElementById('style').value;
  const crewai_enabled = document.getElementById('crewai_enabled').checked;
  const payload = {destinations, start_date, end_date, budget, style, crewai_enabled};
  const res = await fetch('/plan', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok){
    const err = await res.json();
    alert(err.error || 'Error');
    return;
  }
  const data = await res.json();
  document.getElementById('result').style.display = 'block';
  const meta = document.getElementById('meta');
  meta.innerHTML = `<p><strong>Destinations:</strong> ${data.itinerary.destinations.join(', ')} — <strong>Dates:</strong> ${data.itinerary.start_date} to ${data.itinerary.end_date} — <strong>Style:</strong> ${data.itinerary.style}</p>`;
  const itinDiv = document.getElementById('itinerary');
  itinDiv.innerHTML = '';
  data.itinerary.itinerary.forEach(day=>{
    const dayDiv = document.createElement('div');
    dayDiv.className = 'day';
    const title = document.createElement('h4');
    title.textContent = day.date;
    dayDiv.appendChild(title);
    if(day.events.length===0){
      const p = document.createElement('p');
      p.textContent = '(No events scheduled)';
      dayDiv.appendChild(p);
    } else {
      day.events.forEach(ev=>{
        const evDiv = document.createElement('div');
        evDiv.className = 'event';
        evDiv.innerHTML = `<h5>${ev.name} <small>(${ev.destination})</small></h5>
                           <p><em>${ev.type} — ~${ev.duration_hr} hr — $${ev.cost} — Travel from previous: ${ev.travel_from_prev_mins} mins</em></p>
                           <p>${ev.description}</p>
                           <p><strong>Address:</strong> ${ev.address} — <strong>Opening:</strong> ${ev.opening_hours}</p>
                           <p><a href="${ev.map_link}" target="_blank">Open in Maps</a> | <a href="${ev.website}" target="_blank">Search/Website</a></p>`;
        dayDiv.appendChild(evDiv);
      });
    }
    itinDiv.appendChild(dayDiv);
  });
  const packUl = document.getElementById('packing');
  packUl.innerHTML = '';
  data.itinerary.packing.forEach(item=>{
    const li = document.createElement('li');
    li.textContent = item;
    packUl.appendChild(li);
  });
  document.getElementById('budget').textContent = `$${data.itinerary.budget.total.toFixed(2)} — within_budget: ${data.itinerary.budget.within_budget}`;
  document.getElementById('log').textContent = data.log.join('\n');
  window.scrollTo(0, document.body.scrollHeight);
});
