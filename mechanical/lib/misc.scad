
// Simple primatives for generating holes

module hex(side,t){
    /* intersection(){
        cube([side, side, 1.5*t],center=true);
        rotate([0,0,45]) cube([side, side, 1.5*t], center=true);
    } */
    translate([0,0,t/2]) intersection(){
        cube([side, side, t],center=true);
        rotate([0,0,45]) cube([side, side, t], center=true);
    }
}

module M3Nut(t){
    /* dia = 3.5;
    sdia = 9;
    cylinder(3*t, d=dia, center=true);  // M3
    translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver */
    hex(5.6, t);
}

module M2Nut(t){
    hex(4.1, t);
}



/* module M3(t){
    dia = 3.5;
    sdia = 8.5;  // counter sink dia
    cylinder(3*t, d=dia, center=true);  // M3
    translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver
} */

module M2(t){
    dia = 2.5;
    sdia = 6;  // counter sink dia
    cylinder(3*t, d=dia, center=true);  // M2
    /* translate([0,0,2]) cylinder(3*t, d=sdia, center=false);  // screw driver */
    translate([0,0,-1]) M2Nut(3);
}

module M3(t){
    cylinder(h=3*t, d=3.5, center=true);
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
