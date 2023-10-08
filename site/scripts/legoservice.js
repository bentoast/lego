import { Requests } from "./requests.js";

class LegoService {
    static getSingle(setid, callback) {
        Requests.GetRequest('/api/lego.py?action=single&setid=' + setid, null, callback);
    }
  
    static getMultiple(parameters, callback) {
        let paramStr =  Object.keys(parameters)
            .filter(p => parameters[p])
            .map(p => p + '=' + parameters[p])
            .join('&');
        Requests.GetRequest('/api/lego.py?action=multiple&' + paramStr, null, callback);
    }
  
    static updateSet(setid, have, tracked, callback) {
        Requests.GetRequest('/api/lego.py', '{ "action": "update", "parameters": { "setid": ' +
            setid + ', "tracked": ' +
            tracked + ', "have": ' +
            have + '} }', callback);
    }
  }

  class LegoFilter {
    have;
    track;
    setid;
    name;
    price;
    originalprice;
    discount;
    retiring;
    new;

    page = 1;
    count = 25;

    order = 'name';
    asc = true;
  }

  export { LegoService, LegoFilter };