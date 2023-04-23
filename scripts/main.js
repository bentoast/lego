import { LegoSet } from "./legoset.js";
import { LegoService, LegoFilter } from "./legoservice.js";

var finder = {
    sets: [],
    totalCount: 0,
    filter: new LegoFilter(),

    changePage: function(event) {
        //Just guarding against overflows
        if (event.target.dataset.pageChange == 'back' && this.filter.page > 1) {
            this.filter.page--;
        }
        else if (event.target.dataset.pageChange == 'forward' && this.filter.page < this.totalCount / this.filter.count) {
            this.filter.page++;
        }
        this.clearTable();
        this.CreateTable(this.filter);
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
      if (event.target.dataset.filterName == 'order') {
        this.filter.order = event.target.dataset.filterValue;
        this.filter.page = 1;
      }
      else if (event.target.type == 'checkbox') {
        this.filter[event.target.dataset.filterName] = event.target.checked;
        this.filter.page = 1;
      }
      else {
        this.filter[event.target.dataset.filterName] = event.target.value;
        this.filter.page = 1;
      }
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
        let i = 0;
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
          i++;
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
        finder.totalCount = results.total;
        let totalPages = Math.ceil(results.total / finder.filter.count);
        let maxPages = 10;
        if (totalPages < maxPages)
          maxPages = totalPages;
        for (let i = 0; i < maxPages; i++) {
            let pageButton = document.createElement('div');
            pageButton.classList.add('navigation-button');
            if (i + 1 == finder.filter.page) {
              pageButton.classList.add('current-page');
            }
            pageButton.dataset.pageNumber = finder.filter.page + i + 1;
            pageButton.addEventListener('click', finder.goToPage.bind(finder));
            pageButton.appendChild(document.createTextNode(finder.filter.page + i + 1));
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
        }
      }
    },
}

//Initialize the page and the event listeners
finder.init();
document.querySelectorAll('[data-event]').forEach(e => {
  e.addEventListener(e.dataset.event, finder[e.dataset.eventAction].bind(finder));
});