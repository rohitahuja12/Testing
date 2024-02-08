// run the following line to compile
// gcc hdrlib.c -o hdrlib.so -shared -fPIC -O2

#include "hdrlib.h"

void main() {

}

float ave(int a, int b) {
    return (a+b)/2.0;
}

int hdr(const unsigned short* imgs, int imgsX, int imgsY, int imgsN, const int* durs, int sat, float* result) {
    int nonsat_value;
    int sat_duration;
    int nonsat_duration;
    int v;
    float u = 1.0;

    // display the input image stack
    //for (int cc=0; cc<imgsX*imgsY*imgsN; cc++) {
    //    printf("%u ", imgs[cc]);
    //}
    //printf("\n");

	for (int xx=0; xx<imgsX; xx++) {
        for (int yy=0; yy<imgsY; yy++) {
            nonsat_value = 0;
            sat_duration = 0;
            nonsat_duration = 0;
            for (int nn=0; nn<imgsN; nn++) {
                v = imgs[nn*imgsX*imgsY+yy*imgsX+xx];
                if (v>=sat) {
                    sat_duration += durs[nn];
                } else {
                    nonsat_value += v;
                    nonsat_duration += durs[nn];
                }
            }
            result[yy*imgsX+xx] = ((u*nonsat_value)/nonsat_duration) * (nonsat_duration+sat_duration);
        }
    }
    return 0;
}

