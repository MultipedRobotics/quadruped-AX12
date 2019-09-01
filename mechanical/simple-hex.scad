$fn=90;

// https://www.engineersedge.com/hardware/standard_metric_hex_nuts_13728.htm
// m2: d=4    D=4.62
// m3: d=5.5  D=6.35
module hex(D,t){
    x = D/2;
    y = sqrt(3)/2*x;
    pts = [
        [x/2,y],
        [x,0],
        [x/2,-y],
        [-x/2,-y],
        [-x,0],
        [-x/2,y]
    ];
    linear_extrude(height=t){
        polygon(pts);
    }
    echo(2*x);
    echo(2*y);
}

module m3(){
    hex(6.35,3);
}

module m2(){
    hex(4.62,2);
}


//rotate([0,0,0]) hex3(4.62,2);
//circle(15);
m2();