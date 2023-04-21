import { LegoSet } from "./legoset.js";
import { LegoService, LegoFilter } from "./legoservice.js";

var finder = {
    sets: [],
    filter: new LegoFilter(),

    changePage: function(direction) {
        console.log(direction);
    },

    goToPage: function(event) {
        this.filter.page = event.target.dataset.pageNumber;
        this.CreateTable(this.filter);
    },

    clearTable: function() {
      let datarows = document.querySelectorAll("[data-has-data='yes']");
      for (let current of datarows) {
        current.remove();
      }
    },

    changeFilter: function(event) {
      this.filter[event.target.dataset.filterType] = event.target.value;
      this.filter.page = 1;
      this.clearTable();
      this.CreateTable(this.filter);
    },

    findset: function(source) {
      LegoService.getSingle(source['value'], this.addToList.bind(this));
    },

    init: function() {
      this.CreateTable(this.filter);
    },
    
    CreateTable: function(params) {
      this.clearTable();
      //The call back could be taken out of the function and made a separate function
      LegoService.getMultiple(params, function(results) {
        finder.sets = [];

        let navrow = document.getElementById('navigationrow');
        for (var e in results.results)
        {
          var n = new LegoSet(results.results[e]);
          n.CreateRow();
          finder.sets.push(n);
          if (i % 2 == 0)
            n.Element.className = "itemrow";
          else
            n.Element.className = "itemrow striped";
          navrow.parentElement.insertBefore(n.Element, navrow);
        }

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
    },

    addToList: function(results) {
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
    },
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

finder.init();
document.querySelectorAll('[data-event]').forEach(e => {
  e.addEventListener(e.dataset.event, finder[e.dataset.eventAction].bind(finder));
});