import { LegoService } from "./legoservice";

class LegoSet {
    Element;

    columns = ["setid", "name", "price", "originalprice", "discount", "retiring", "new"];

    constructor(core) {
        this['tracked'] = core['tracked'];
        this['have'] = core['have'];

        for (let current of this.columns) {
            this[current] = core[current];
        }
    }

    CreateRow() {
        this.Element = document.createElement('tr');
        this.Element.dataset.hasData = "yes";

        for (let current of ['have', 'tracked']) {
            let cell = document.createElement('td');
            let check = document.createElement('input');
            check['type'] = 'checkbox';
            check['checked'] = this[current];
            check.dataset.checkType = current;
            check.addEventListener('change', this.ChangeTrack.bind(this));
            cell.appendChild(check);
            this.Element.append(cell);
        }

        for (let current of this.columns) {
            let cell = document.createElement('td');
            if (current == "name")
            {
                let anchor = document.createElement('a');
                anchor['href'] = 'https://lego.com/en-us/product/' + this['setid'];
                anchor['target'] = '_blank';
                anchor.innerText = this[current];
                cell.appendChild(anchor);
            }
            else
            {
                let string = this[current];
                if (current == 'retiring' || current == 'new')
                {
                    cell['style'] = 'text-align: center;';
                    if (this[current] == '1')
                        string = '\u2705';
                    else
                        string = '';
                }
                else if (current == 'discount')
                {
                    cell.classList.add('pricecell');
                    if (this[current] > 0)
                        string = (this[current] * 100) + '%';
                    else
                        string = '';
                }
                else if (current == 'price' || current == 'originalprice')
                {
                    cell.classList.add('pricecell');
                    string = '$' + this[current];
                }
                cell.appendChild(document.createTextNode(string));
            }
            this.Element.appendChild(cell);
        }
    }

    ChangeTrack(event) {
        this[event.target.dataset.checkType] = event.target.checked;
        LegoService.updateSet(
            this['setid'],
            this['have'],
            this['tracked'], this.Saved.bind(this));
    }

    Saved() {
        
    }
}

export { LegoSet };