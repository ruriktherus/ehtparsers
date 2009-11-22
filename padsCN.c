#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>

#define PI 3.1415926536
void latlon2xyz(double,double,double,double*,double*,double*);

int main(int argc, char *argv[])
{ double xyz1[3],gpsLat,gpsLon,gpsHgt,lat,lon,x1,y1,z1,x2,y2,z2;
 int pad1;
 for(pad1 = 1; pad1 <24; pad1++){
   xyz1[0] = 0; xyz1[1] = 0; xyz1[2] = 0;
   if(pad1 == 23) { xyz1[0] = -17.91543; 
                    xyz1[1] = -59.55809;  
		    xyz1[2] = 30.06989; } 
   if(pad1 == 9) {  xyz1[0] = -6.39984;  
                    xyz1[1] = -68.00177;
		    xyz1[2] = 3.63823; }
   if(pad1 == 5) {  xyz1[0] = -5.70168;
                    xyz1[1] = -18.98415;
		    xyz1[2] = 15.61046; }
   if(pad1 == 7) {  xyz1[0] = 5.22979;  
                    xyz1[1] = -20.07732;
		    xyz1[2] = -14.84317; }
   if(pad1 == 4) {  xyz1[0] = -0.50892;  
                    xyz1[1] = -25.15161;
		    xyz1[2] = 1.28166; }
   if(pad1 == 16) { xyz1[0] = -42.59886;  
                    xyz1[1] = -71.54986;
		    xyz1[2] = 86.19689; }
   if(pad1 == 8) {  xyz1[0] = 4.44176;  
                    xyz1[1] = -63.8752;
		    xyz1[2] = -21.83506; }
   if(pad1 == 1) {xyz1[0] = 0; xyz1[1] = 0; xyz1[2] = 0; }

   gpsLat = 19.823797; gpsLon = -155.471371; gpsHgt = 
					       4205.0;
   latlon2xyz(gpsLat, gpsLon, gpsHgt, &x1, &y1, &z1);
   //                        printf("x %f y %f z %f\n",x1,y1,z1);
   x1 = -5464555.493; y1=-2492927.989; 
   z1=2150797.176;    // pad1 posn
   gpsLon = atan2(y1,x1)*180.0/PI;
   //                        printf("gpsLon %f\n",gpsLon);
   lat = gpsLat*PI/180.0; lon=gpsLon*PI/180.0;
   x2 = x1 + xyz1[0]* cos(lon) - xyz1[1]*sin(lon);
   y2 = y1 + xyz1[1]* cos(lon) + xyz1[0]*sin(lon);
   z2 = z1 + xyz1[2];
   if(xyz1[0] !=0 || pad1==1)
     printf("p%02i x=%10.3f y=%10.3f z=%10.3f %7.3f %7.3f %7.3f\n",pad1,x2,y2,z2,xyz1[0],xyz1[1],xyz1[2]);
 }
}

/**============================================================================
 ** routine to convert latitude and longitude to x,y,z coords
 ** lat,lon in degrees, lon +v east hgt in meters, outputs x,y,z in meters

 **==========================================================================*/
void latlon2xyz(double lat, double lon, double hgt, double *x, double *y, 
		double *z)
{
  double deg_to_rad, a, e, f, n;
  deg_to_rad = PI / 180.0;
  f = 1.0 / 298.257223563;    /* WGS 84 */
  e = 2.0 * f - f * f;
  a = 6378137.0;              /* WGS 84 earth radius */

  n = a / sqrt(1.0 - e * sin(lat * deg_to_rad) * sin(lat * deg_to_rad));
  *x = (n + hgt) * cos(lat * deg_to_rad) * cos(lon * deg_to_rad);
  *y = (n + hgt) * cos(lat * deg_to_rad) * sin(lon * deg_to_rad);
  *z = (n * (1.0 - e) + hgt) * sin(lat * deg_to_rad);

}
