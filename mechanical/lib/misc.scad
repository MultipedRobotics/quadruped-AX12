
// Simple primatives for generating holes

module hexold(side,t){
    /* intersection(){
        cube([side, side, 1.5*t],center=true);
        rotate([0,0,45]) cube([side, side, 1.5*t], center=true);
    } */
    translate([0,0,t/2]) intersection(){
        cube([side, side, t],center=true);
        rotate([0,0,45]) cube([side, side, t], center=true);
    }
}

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
    //echo(2*x);
    //echo(2*y);
}

module M3Nut(t){
    /* dia = 3.5;
    sdia = 9;
    cylinder(3*t, d=dia, center=true);  // M3
    translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver */
    hex(6.4, t);
}

module M2Nut(t){
    hex(4.65, t);
}



/* module M3(t){
    dia = 3.5;
    sdia = 8.5;  // counter sink dia
    cylinder(3*t, d=dia, center=true);  // M3
    translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver
} */

module M2(t){
    dia = 2.2;
    sdia = 6;  // counter sink dia
    cylinder(3*t, d=dia, center=true);  // M2
    /* translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver */
    translate([0,0,-1]) M2Nut(3);
}

module M3(t){
    cylinder(h=3*t, d=3.3, center=true);
    translate([0,0,2]) cylinder(h=3*t, d=7, center=false);
}

/* module M2(t){
    cylinder(h=40, d=2.6, center=false);
} */

/* module holes(t){
    // M3 3.3 mm
    M3(t);

    // M2 2.3 mm
    // dia = 2.3;
    translate([8,0,0]) M2(t);
    translate([-8,0,0]) M2(t);
    translate([0,8,0]) M2(t);
    translate([0,-8,0]) M2(t);
}

module pulley(dia=24, thick=3, cen=false){
    cylinder(thick,d=dia,center=cen);
} */
