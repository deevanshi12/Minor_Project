const ctx = document.getElementById('chart');

new Chart(ctx, {

type: 'line',

data: {

labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],

datasets: [{
label: 'Mood Level',
data: [6,7,5,8,7,9,8],
borderColor: '#4f46e5',
fill: false
}]

}

});
