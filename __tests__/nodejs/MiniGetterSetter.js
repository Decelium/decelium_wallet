class MiniGetterSetter {
    constructor() {
        this.vals = {};
    }

    set_value(args, settings) {
        if (!args.hasOwnProperty('key') || !args.hasOwnProperty('val')) {
            throw new Error('Missing required arguments: key and/or val');
        }
        console.log('setting value ' + args.val);
        this.vals[args.key] = args.val;
        return true;
    }

    get_value(args, settings) {
        if (this.vals.hasOwnProperty(args.key)) {
            console.log('getting value ' + args.key);
            return this.vals[args.key];
        }
        return this.vals;
    }

    get_all(args, settings) {
        return this.vals;
    }
}

export default  MiniGetterSetter;
export {MiniGetterSetter};
