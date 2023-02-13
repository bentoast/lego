var finder = {
    changePage: function(direction) {
        console.log(direction);
    },

    goToPage: function(event) {
        console.log(event.target.dataset.pageNumber);
    },
}

var sets = [];

function GetRequest(url, data, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
    {
      var j = JSON.parse(this.responseText);
      callback(j);
    }
  }

  if (data)
  {
    xhttp.open("POST", url, true);
    xhttp.send(data);
  }
  else
  {
    xhttp.open("GET", url, true);
    xhttp.send();
  }
}

function CreateTable(url, table) {
  GetRequest(url, null, function(results) {
    for (var e in results.results)
    {
      var n = new LegoSet(results.results[e]);
      n.CreateRow();
      sets.push(n);
    }
    
    sortby('name');

    let lastButton = document.getElementById('forwardButton');
    let totalPages = Math.ceil(results.total / 25);
    for (let i = 0; i < totalPages; i++) {
        let pageButton = document.createElement('div');
        pageButton.classList.add('navigation-button');
        pageButton.addEventListener('click', finder.goToPage.bind(finder));
        pageButton.appendChild(document.createTextNode(i + 1));
        lastButton.parentElement.insertBefore(pageButton, lastButton);
    }
  });
}

function filterTable() {
  for (var i in sets)
  {
    sets[i].Element.remove();
  }
  
  var filteredSet = sets;
  
  var currentFilter = document.getElementById('havefilter');
  if (currentFilter['checked'])
    filteredSet = filteredSet.filter(f => f['have']);
  currentFilter = document.getElementById('trackedfilter');
  if (currentFilter['checked'])
    filteredSet = filteredSet.filter(f => f['tracked']);
  currentFilter = document.getElementById('setidfilter');
  if (currentFilter['value'])
    filteredSet = filteredSet.filter(f => f['setid'].toLowerCase().includes(currentFilter['value'].toLowerCase()));
  currentFilter = document.getElementById('namefilter');
  if (currentFilter['value'])
    filteredSet = filteredSet.filter(f => f['name'].toLowerCase().includes(currentFilter['value'].toLowerCase()));
  currentFilter = document.getElementById('pricefilter');
  if (currentFilter['value'])
    filteredSet = filteredSet.filter(f => f['price'] <= currentFilter['value']);
  currentFilter = document.getElementById('originalfilter');
  if (currentFilter['value'])
    filteredSet = filteredSet.filter(f => f['originalprice'] <= currentFilter['value']);
  currentFilter = document.getElementById('discountfilter');
  if (currentFilter['value'])
    filteredSet = filteredSet.filter(f => f['discount'] >= (currentFilter['value'] / 100));
  currentFilter = document.getElementById('retiringfilter');
  if (currentFilter['checked'])
    filteredSet = filteredSet.filter(f => f['retiring']);
  currentFilter = document.getElementById('newfilter');
  if (currentFilter['checked'])
    filteredSet = filteredSet.filter(f => f['new']);
  
  let navrow = document.getElementById('navigationrow');
  for (var i in filteredSet)
  {
    var n = filteredSet[i];
    if (i % 2 == 0)
      n.Element.className = "itemrow";
    else
      n.Element.className = "itemrow striped";
    navrow.parentElement.insertBefore(n.Element, navrow);
  }
}

var sortAttribute = '';
function sortby(attribute) {
  if (sortAttribute != attribute)
  {
    sortAttribute = attribute;
    sets.sort(function(a, b) {
      if (a[attribute] < b[attribute])
        return -1;
      if (a[attribute] > b[attribute])
        return 1;
      return 0;
    });
  }
  else
  {
    sortAttribute = '';
    sets.sort(function(b, a) {
      if (a[attribute] < b[attribute])
        return -1;
      if (a[attribute] > b[attribute])
        return 1;
      return 0;
    });
  }
  filterTable();
}

function findset(source) {
  GetRequest('lego.py?action=check&setid=' + source['value'], null, addToList);
}

function addToList(results) {
  if (results.length > 0)
  {
    var r = results[0];
    var found = sets.filter(f => f['setid'] == r['setid']);
    if (found.length == 0)
    {
      var curSet = new LegoSet(r);
      curSet.CreateRow();
      sets.push(curSet);
      filterTable();
    }
  }
}