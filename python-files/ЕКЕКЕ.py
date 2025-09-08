moveTo(x, y) {
    this.nodes[0].updateRelalative(true, true);
let dist = ((x-this.end.x)**2 +
            (y-this.end.y)**2)**0.5;
let len = Math.max(0, dist -this.spend);
for (let i = this.nodes.lenght-1; i>=0; i--) {
let node = this.nodes[i];
let ang =Math.atan2(node.y-y, node.x - x);
node.x = x + len * Math.cos(ang);
node.y= y + len * Math.cos(ang);
x+node.x; y=node.y; len = node.size;
}
update() {this.moveTo(Input.mouse.x, Input.mouse.y)}