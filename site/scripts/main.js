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
        this.filter.page = parseInt(event.target.dataset.pageNumber);
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
        if (this.filter.order == event.target.dataset.filterValue) {
          this.filter.asc = !this.filter.asc;
        }
        else {
          this.filter.order = event.target.dataset.filterValue;
          this.filter.page = 1;
          this.filter.asc = true;
        }
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
      LegoService.getSingle(source.target.value, this.addToList.bind(this));
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
        let pages = finder.getPageList();
        for (let currentPage of pages) {
            let pageButton = document.createElement('div');
            pageButton.classList.add('navigation-button');
            if (currentPage == finder.filter.page) {
              pageButton.classList.add('current-page');
            }
            pageButton.dataset.pageNumber = currentPage;
            pageButton.addEventListener('click', finder.goToPage.bind(finder));
            pageButton.appendChild(document.createTextNode(currentPage));
            lastButton.parentElement.insertBefore(pageButton, lastButton);
        }
      });
    },

    getPageList: function() {
      let pages = [];
      let totalPages = Math.ceil(this.totalCount / this.filter.count);
      if (totalPages <= 10) {
        for (let current = 1; current <= totalPages; current++)
          pages.push(current + '');
        return pages;
      }

      pages.push('1');
      let minWindow = this.filter.page - 2;
      let maxWindow = this.filter.page + 3;
      if (minWindow < 3) {
        let distance = 3 - minWindow;
        minWindow += distance;
        maxWindow += distance;
      }
      else if (maxWindow > totalPages - 2) {
        let distance = maxWindow - (totalPages - 2);
        minWindow -= distance;
        maxWindow -= distance;
      }
      if (minWindow > 3)
        pages.push('...');
      else
        pages.push('2');
      for (let current = minWindow; current <= maxWindow; current++)
        pages.push(current + '');
      if (maxWindow < totalPages - 2)
        pages.push('...');
      else
        pages.push((totalPages - 1) + '');
      pages.push(totalPages + '');
      return pages;
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