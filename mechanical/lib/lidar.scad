

module rplidar(){
    // sort of center mass
    color("gray") rotate([90,0,180]) translate([-40,0,-35]) import("parts/rplidar.STL");
}

// rplidar();

module x4lidar(){
    // sort of center mass
    color("gray") rotate([0,0,180]) translate([0,0,70]) import("parts/X4.stl");
}

/* x4lidar(); */
