import { LegoService } from "./legoservice.js";

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
                let nameSpan = document.createElement('span');
                nameSpan.innerText = this[current];
                cell.appendChild(nameSpan);

                let legoAnchor = document.createElement('a');
                legoAnchor['href'] = 'https://lego.com/en-us/product/' + this['setid'];
                legoAnchor['target'] = '_blank';
                legoAnchor.innerText = '(Lego)';
                cell.appendChild(legoAnchor);

                let blAnchor = document.createElement('a');
                blAnchor['href'] = 'https://www.bricklink.com/v2/catalog/catalogitem.page?S=' + this['setid'];
                blAnchor['target'] = '_blank';
                blAnchor.innerText = '(BL)';
                cell.appendChild(blAnchor);

                let bsAnchor = document.createElement('a');
                bsAnchor['href'] = 'https://www.brickset.com/sets/' + this['setid'];
                bsAnchor['target'] = '_blank';
                bsAnchor.innerText = '(BS)';
                cell.appendChild(bsAnchor);
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