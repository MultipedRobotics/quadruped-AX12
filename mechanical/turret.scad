$fn = 90;

// library folder
use <lib/robotis_parts.scad>;
use <lib/misc.scad>;
use <lib/pi.scad>;
use <lib/lidar.scad>;


module piFootPrint(depth=10){
    dx = 58;
    dy = 49;
    translate([-dx/2,-dy/2,0]){
        M2(20);
        translate([dx,0,0]) M2(20);
        translate([0,dy,0]) M2(20);
        translate([dx,dy,0]) M2(20);
    }
}

module M2standoff(x,y,z,h){
    dia = 2.5;
    wide = 3;

    translate([x,y,z]) difference(){
        cylinder(h=h, d=dia+wide);
        cylinder(h=4*h, d=dia, center=true);
    }
}

module cameramount(thick){
    offset = 15;
    translate([0,-3,0]){  // move to avoid screw holes
        // connects to base plate
        difference(){
            translate([-49/2,0,0]) cube([49, 15, thick]);
            translate([-25/2,-1,-1]) cube([25, 20, 2*thick]); // screw cutout
        }
        // camera mount back
        difference()
        {
            translate([-49/2,0,0]) cube([49, 4, 30+offset]);

            translate([-49/2+3+2,-1,3+offset+2]) rotate([90,0,0]){
                M3(6);
                translate([0,0,-6]) M3Nut(3);
            }  // bottom left
            translate([-49/2+3+2,-1,3+offset+20+2]) rotate([90,0,0]) {
                M3(6);
                translate([0,0,-6]) M3Nut(3);
            }  // top left
            translate([49/2-7+2,-1,3+offset+2]) rotate([90,0,0]) {
                M3(6);
                translate([0,0,-6]) M3Nut(3);
            } // bottom right
            translate([49/2-7+2,-1,3+offset+20+2]) rotate([90,0,0]) {
                M3(6);
                translate([0,0,-6]) M3Nut(3);
            } // top right

            translate([0,0,20]) rotate([90,0,0]) {
                cylinder(h=10, d=25, center=true); // arch
            }

            translate([-25/2,-1,-1]) cube([25, 10, 20]);  // cable/sd card cutout
        }
        // curved edges
        difference(){
            translate([-49/2,0,4]) cube([49, 8, 5]);
            translate([-49/2-1,5+4,4+5]) rotate([0,90,0]) cylinder(h=55, d=10);
            translate([-25/2,-1,-1]) cube([25, 20, 40]); // screw cutout
        }
    }
}

module rpi_base(){
    difference()
    {
        // main deck
        cylinder(h=4, d=100);

        // cable cutouts
        translate([-12.5,-50,-1]) cube([25,11,20], center=false); // front
        translate([0,-40,0]) cylinder(h=10, d=25, center=true); // front curve
        translate([0,-2.55,0]) cube([70,30,20], center=true); // side cable runs
        translate([0,10,0]) cylinder(h=20, d=40, center=true);

        // alt imu mount point
        y = 5;
        translate([-38, 23+y, 0]) M2(20);
        translate([-38, y, 0]) M2(20);

        // screws to bottom (legs)
        translate([50-5/2-1, 0, 0]) {M3(20);}
        translate([-50+5/2+1, 0, 0]) {M3(20);}
        translate([0, 50-5/2-1, 0]) {M3(20);}
        translate([0, -50+5/2+1, 0]) {M3(20);}

        // screws to top (lidar)
        rotate([0,180,45]) translate([0,0,-4]){
            rotate([0,0,20]) translate([50-5/2-1, 0, 0]) M3(20);
            translate([-50+5/2+1, 0, 0]) M3(20);
            translate([0, 50-5/2-1, 0]) M3(20);
            rotate([0,0,-20]) translate([0, -50+5/2+1, 0]) M3(20);
        }

        rotate([0,0,90]) translate([-10,0,0]) piFootPrint();
    }

    // imu standoffs
    height = 3;  // height above plate
    y = 5;
    M2standoff(-38,23+y,4,height);
    M2standoff(-38,y,4,height);

    // pi standoffs
    dx = 58;
    dy = 49;
    rotate([0,0,90]) translate([-dx/2,-dy/2,0]) {
        M2standoff(dx-10,0,4,height);
        M2standoff(-10,0,4,height);
        M2standoff(dx-10,dy,4,height);
        M2standoff(-10,dy,4,height);
    }

    translate([0,-55,0]) cameramount(4);
}

module lidar_base(){
    dia = 100;
    difference(){
        cylinder(h=4, d=100);
        cylinder(h=10, d=40, center=true);

        // screws to rpi deck
        m3d = 6;
        translate([50-5/2-1, 0, 0]) M3Nut(20);
        rotate([0,0,-20]) translate([-50+5/2+1, 0, 0]) M3Nut(20);
        translate([0, 50-5/2-1, 0]) M3Nut(20);
        rotate([0,0,20]) translate([0, -50+5/2+1, 0]) M3Nut(20);

        // ydlidar/lds-01 lidar mount
        rotate([0,180,45]) translate([3,0,-4]){
            translate([22,31,0]) M3(20);
            translate([22,-31,0]) M3(20);
            translate([-35,25,0]) M3(20);
            translate([-35,-25,0]) M3(20);
        }

        // rpylidar - tbd

        // hokuyo urg mount
        rotate([0,180,45]) translate([0,0,-4]){
            translate([20,20,0]) M3(20);
            translate([20,-20,0]) M3(20);
            translate([-20,20,0]) M3(20);
            translate([-20,-20,0]) M3(20);
        }

        // skeletonizing
        translate([dia/3+4, dia/3+4, -2]) rotate([0,0,-45]) scale([1.2,.85,1]) cylinder(h=10, d=50); // back
        translate([-dia/4-5, dia/2.5, -2]) rotate([0,0,35]) scale([.90,.75,1]) cylinder(h=10, d=50); // right
        translate([dia/2.5, -dia/4-5, -2]) rotate([0,0,35]) scale([.90,.75,1]) cylinder(h=10, d=50); // left
        translate([-dia/3, -dia/3, -2]) rotate([0,0,-45]) scale([1.75,.70,1]) cylinder(h=10, d=50); // front
    }
}

COLOR1 = "red";
color(COLOR1) rpi_base();
translate([0,-60,20]) rotate([90,0,0]) picamera();
rotate([0,0,90]) translate([2,0,6]) rpi3();
translate([0,0,30]) rotate([0,0,45]) color(COLOR1) lidar_base();
translate([0,0,34]) rotate([0,0,-90]) x4lidar();
