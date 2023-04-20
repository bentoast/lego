import { LegoSet } from "./legoset.js";
import { LegoService } from "./legoservice.js";

var finder = {
    page: 1,
    pageSize: 25,

    changePage: function(direction) {
        console.log(direction);
    },

    goToPage: function(event) {
        this.page = event.target.dataset.pageNumber;
        let params = { 'count': this.pageSize, 'page': this.page };
        CreateTable(params);
    },

    clearTable: function() {
      let datarows = document.querySelectorAll("[data-has-data='yes']");
      for (let current of datarows) {
        current.remove();
      }
    },

    changeFilter: function(event) {
    },
}

var sets = [];

function CreateTable(params) {
  finder.clearTable();
  //The call back could be taken out of the function and made a separate function
  LegoService.getMultiple(params, function(results) {
    sets = [];
    for (var e in results.results)
    {
      var n = new LegoSet(results.results[e]);
      n.CreateRow();
      sets.push(n);
    }
    
    sortby('name');

    let navElement = document.getElementById('backButton').parentElement;
    let collected = [];
    for (let currentNav in navElement.childNodes) {
        if (navElement.childNodes[currentNav].dataset && navElement.childNodes[currentNav].dataset.pageNumber) {
            collected.push(navElement.childNodes[currentNav]);
        }
    }
    for (let currentElem of collected) {
        currentElem.remove();
    }

    let lastButton = document.getElementById('forwardButton');
    let totalPages = Math.ceil(results.total / 25);
    for (let i = 0; i < totalPages; i++) {
        let pageButton = document.createElement('div');
        pageButton.classList.add('navigation-button');
        pageButton.dataset.pageNumber = i + 1;
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
  
  //All these need to be collected and sent by "GetMultiple"
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
//This also needs to be part of the "GetMultiple" saga
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
  LegoService.getSingle(source['value'], addToList);
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

function init() {
  CreateTable({"count": finder.pageSize, "page": finder.page });
}

document.body.addEventListener('load', init());

document.querySelectorAll('[data-filter-action').forEach(e => {
  e.addEventListener(e.dataset.filterAction, finder.changeFilter.bind(finder));
});

export { finder, CreateTable, filterTable, sortby, findset, addToList }