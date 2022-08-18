#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include <iostream>
#include <sstream>

#define NULLRUN_SAMPLE_COUNT 100
#define ADDR_CA 0x4a
#define ADDR_CB 0x48
#define ADDR_CC 0x49
#define ADDR_V 0x48

#define I2C_FILE_C "/dev/i2c-0"
#define I2C_FILE_V "/dev/i2c-1"
#define OUT_FILE "/tmp/phase"
#define CONFIG_REG 0x01
#define READ_REG 0x00
// #define SPEED_CONFIG 0x63
#define SPEED_CONFIG 0x83
// #define SPEED_CONFIG 0xA0

const char VOLTAGE_CONFIG[] = {CONFIG_REG, 0x00, SPEED_CONFIG};
const char CURENT_CONFIG_01[] = {CONFIG_REG, 0x08, SPEED_CONFIG};
const char CURENT_CONFIG_23[] = {CONFIG_REG, 0x38, SPEED_CONFIG};
const char NULL_CONFIG[] = {CONFIG_REG, 0x1, 0x83};
const char READ_CONF[] = {READ_REG};

typedef struct {
    FILE* outDesc;
    int cBus;
    int vBus;
    int sampleCount;
} Common;

typedef struct {
    unsigned char* const cIn;
    unsigned char* const cOut;
    unsigned char* const v;
    clock_t (*const timePoints)[3];
    clock_t startPoint;
    long long int startTime;
    long long int endTime;
} PhData;

void outputVal(Common env, int phId, PhData phaseList) {
    fprintf(env.outDesc, ">%d,%d,%lld,%lld\n", phId, env.sampleCount,
            phaseList.startTime, phaseList.endTime);
    // clock_t lastTimePoint = phaseList.startPoint;
    double const msDivConst = CLOCKS_PER_SEC / 1000;
    for (int sampleId = 0; sampleId < env.sampleCount; sampleId++) {
        unsigned int cIn = (((unsigned int)phaseList.cIn[sampleId * 2]) << 8) +
                           (unsigned int)phaseList.cIn[sampleId * 2 + 1];
        unsigned int cOut =
            (((unsigned int)phaseList.cOut[sampleId * 2]) << 8) +
            (unsigned int)phaseList.cOut[sampleId * 2 + 1];
        unsigned int v = (((unsigned int)phaseList.v[sampleId * 2]) << 8) +
                         (unsigned int)phaseList.v[sampleId * 2 + 1];

        // double tSpanIn = lastTimePoint - phaseList.timePoints[sampleId][0];
        // double tSpanV = phaseList.timePoints[sampleId][0] - phaseList.timePoints[sampleId][1];
        // double tSpanOut = phaseList.timePoints[sampleId][1] - phaseList.timePoints[sampleId][2];
        // fprintf(env.outDesc, "=%u,%u,%u,%.0f,%.0f,%.0f\n", cIn, cOut, v, tSpanIn, tSpanOut, tSpanV);
        double tIn = (phaseList.timePoints[sampleId][0] - phaseList.startPoint) / msDivConst;
        double tV = (phaseList.timePoints[sampleId][1] - phaseList.startPoint) / msDivConst;
        double tOut = (phaseList.timePoints[sampleId][2] - phaseList.startPoint) / msDivConst;
        fprintf(env.outDesc, "=%u,%u,%u,%f,%f,%f\n", cIn, cOut, v, tIn, tOut, tV);
    }
}

void readIO_nullRun(Common env, unsigned char addrA, unsigned char addrB,
                    int runNum) {
    unsigned char* tmp = (unsigned char*)malloc(2 * sizeof(char));
    for (int sampleId = 0; sampleId < runNum; sampleId++) {
        ioctl(env.cBus, I2C_SLAVE, addrA);
        read(env.cBus, tmp, 2);
        read(env.vBus, tmp, 2);
        ioctl(env.cBus, I2C_SLAVE, addrB);
        read(env.cBus, tmp, 2);
    }
    // free(tmp); //Small amount of mem, do not switch contexts
}
void readIO(Common env, unsigned char addrA, unsigned char addrB,
            PhData* retRef) {
    PhData ret = *retRef;
    ioctl(env.cBus, I2C_SLAVE, addrA);
    write(env.cBus, CURENT_CONFIG_01, 3);
    write(env.cBus, READ_CONF, 1);
    ioctl(env.cBus, I2C_SLAVE, addrB);
    write(env.cBus, CURENT_CONFIG_23, 3);
    write(env.cBus, READ_CONF, 1);

    struct timeval start, end;
    clock_t subStart, subEnd;
    gettimeofday(&start, NULL);
    ret.startPoint = clock();
    for (int sampleId = 0; sampleId < env.sampleCount; sampleId++) {
        /* subStart = clock(); */

        // read in
        ioctl(env.cBus, I2C_SLAVE, addrA);
        // write(env.cBus, READ_CONF, 1);
        read(env.cBus, &(ret.cOut[sampleId * 2]), 2);
        ret.timePoints[sampleId][0] = clock();

        /* subEnd = clock();
        printf("A: %.0f; ",
               (double)(subEnd - subStart) / CLOCKS_PER_SEC * 1000000);
        subStart = clock(); */

        // read voltage
        // write(env.vBus, READ_CONF, 1);
        read(env.vBus, &(ret.v[sampleId * 2]), 2);
        ret.timePoints[sampleId][1] = clock();

        /* subEnd = clock();
        printf("B: %.0f; ",
               (double)(subEnd - subStart) / CLOCKS_PER_SEC * 1000000);
        subStart = clock(); */

        // read out
        ioctl(env.cBus, I2C_SLAVE, addrB);
        // write(env.cBus, READ_CONF, 1);
        read(env.cBus, &(ret.cIn[sampleId * 2]), 2);
        ret.timePoints[sampleId][2] = clock();

        /* subEnd = clock();
        printf("C: %.0f\n",
               (double)(subEnd - subStart) / CLOCKS_PER_SEC * 1000000); */
    }
    gettimeofday(&end, NULL);
    retRef->startTime = start.tv_sec * 1000LL + start.tv_usec / 1000;
    retRef->endTime = end.tv_sec * 1000LL + end.tv_usec / 1000;
    // printf("T: %lld\n", retRef->endTime - retRef->startTime);
}

PhData readIOGen(Common env, unsigned char addrA, unsigned char addrB) {
    unsigned char* rec_cIn =
        (unsigned char*)malloc(env.sampleCount * 2 * sizeof(char));
    unsigned char* rec_cOut =
        (unsigned char*)malloc(env.sampleCount * 2 * sizeof(char));
    unsigned char* rec_v =
        (unsigned char*)malloc(env.sampleCount * 2 * sizeof(char));
    clock_t(*timePoints)[3] =
        (clock_t(*)[3])malloc(env.sampleCount * sizeof(clock_t[3]));
    PhData ret = {rec_cIn, rec_cOut, rec_v, timePoints};
    readIO(env, addrA, addrB, &ret);
    return ret;
}
void beFree(PhData data) {
    free(data.cIn);
    free(data.cOut);
    free(data.v);
    free(data.timePoints);
}

int runIO(Common env) {
    char nullBuff[2] = {0};
    // Test avalibility
    if (ioctl(env.vBus, I2C_SLAVE, ADDR_V) < 0 ||
        write(env.vBus, VOLTAGE_CONFIG, 3) < 0 ||
        write(env.vBus, READ_CONF, 1) < 0 || read(env.vBus, nullBuff, 2) != 2 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CA) < 0 ||
        write(env.cBus, CURENT_CONFIG_01, 3) < 0 ||
        write(env.cBus, READ_CONF, 1) < 0 || read(env.cBus, nullBuff, 2) != 2 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CB) < 0 ||
        write(env.cBus, CURENT_CONFIG_01, 3) < 0 ||
        write(env.cBus, READ_CONF, 1) < 0 || read(env.cBus, nullBuff, 2) != 2 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CC) < 0 ||
        write(env.cBus, CURENT_CONFIG_01, 3) < 0 ||
        write(env.cBus, READ_CONF, 1) < 0 || read(env.cBus, nullBuff, 2) != 2) {
        return -1;
    }
    readIO_nullRun(env, ADDR_CA, ADDR_CB, NULLRUN_SAMPLE_COUNT); // for std 
    /* PhData ph2 = readIOGen(env, ADDR_CA, ADDR_CB);  // SWITCHED !!
    PhData ph1 = readIOGen(env, ADDR_CC, ADDR_CA);  // SWITCHED !!
    PhData ph3 = readIOGen(env, ADDR_CB, ADDR_CC); */
    PhData ph1 = readIOGen(env, ADDR_CA, ADDR_CB);
    PhData ph2 = readIOGen(env, ADDR_CB, ADDR_CC);
    PhData ph3 = readIOGen(env, ADDR_CC, ADDR_CA);
    // printf("Load FIN\n");
    outputVal(env, 0, ph1);
    outputVal(env, 1, ph2);
    outputVal(env, 2, ph3);
    beFree(ph1);
    beFree(ph2);
    beFree(ph3);

    if (write(env.vBus, NULL_CONFIG, 3) < 0 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CA) < 0 ||
        write(env.cBus, NULL_CONFIG, 3) < 0 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CB) < 0 ||
        write(env.cBus, NULL_CONFIG, 3) < 0 ||
        ioctl(env.cBus, I2C_SLAVE, ADDR_CC) < 0 ||
        write(env.cBus, NULL_CONFIG, 3) < 0) {
        return -1;
    }

    return 0;
}

int main(int argc, char const* argv[]) {
    if (argc < 2) {
        printf("End with %d\n", 10);
        return 10;
    }
    // SET NIDE VALUE
    id_t pid = getpid();
    int trgNiceVal = -20;
    int ret = nice(trgNiceVal);
    // int ret = setpriority(PRIO_PROCESS, pid, -19); // WHY NOT WORKING (TO DO)
    // int procRealPrior = getpriority(PRIO_PROCESS, pid);
    // printf("PID UID ret: %d %d %d %d\n", getpid(), getuid(), ret,
    // procRealPrior);
    if (ret != trgNiceVal) {
        printf("End with %d\n", 20);
        return 20;
    }

    Common env;
    env.cBus = open(I2C_FILE_C, O_RDWR);
    env.vBus = open(I2C_FILE_V, O_RDWR);
    env.outDesc = fopen(OUT_FILE, "w");
    env.sampleCount = atoi(argv[1]);

    int retCode = runIO(env);
    printf("End with %d\n", retCode);

    close(env.cBus);
    close(env.vBus);
    fclose(env.outDesc);

    return retCode;
}
