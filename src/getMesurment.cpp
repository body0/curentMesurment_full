#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <unistd.h>

#include <iostream>
#include <sstream>

#include <unistd.h>
#include <sys/resource.h>

#define SAMPLE_COUNT 300
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
} Common;

typedef struct {
    unsigned char* const cIn;
    unsigned char* const cOut;
    unsigned char* const v;
    long long int startTime;
    long long int endTime;
} PhData;

void outputVal(Common env, int phId, PhData phaseList) {
    fprintf(env.outDesc, ">%d,%d,%lld,%lld\n", phId, SAMPLE_COUNT, phaseList.startTime, phaseList.endTime);
    for (int sampleId = 0; sampleId < SAMPLE_COUNT; sampleId++) {
        unsigned int cIn = (((unsigned int)phaseList.cIn[sampleId * 2]) << 8) +
                           (unsigned int)phaseList.cIn[sampleId * 2 + 1];
        unsigned int cOut =
            (((unsigned int)phaseList.cOut[sampleId * 2]) << 8) +
            (unsigned int)phaseList.cOut[sampleId * 2 + 1];
        unsigned int v = (((unsigned int)phaseList.v[sampleId * 2]) << 8) +
                         (unsigned int)phaseList.v[sampleId * 2 + 1];

        fprintf(env.outDesc, "=%u,%u,%u\n", cIn, cOut, v);
    }
}

void readIO(Common env, unsigned char addrA, unsigned char addrB, PhData* retRef) {
    PhData ret = *retRef;
    ioctl(env.cBus, I2C_SLAVE, addrA);
    write(env.cBus, CURENT_CONFIG_01, 3);
    write(env.cBus, READ_CONF, 1);
    ioctl(env.cBus, I2C_SLAVE, addrB);
    write(env.cBus, CURENT_CONFIG_23, 3);
    write(env.cBus, READ_CONF, 1);

    struct timeval start;
    struct timeval end;
    gettimeofday(&start, NULL);
    for (int sampleId = 0; sampleId < SAMPLE_COUNT; sampleId++) {
        // read in
        ioctl(env.cBus, I2C_SLAVE, addrA);
        // write(env.cBus, READ_CONF, 1);
        read(env.cBus, &(ret.cOut[sampleId * 2]), 2);

        // read voltage
        // write(env.vBus, READ_CONF, 1);
        read(env.vBus, &(ret.v[sampleId * 2]), 2);

        // read out
        ioctl(env.cBus, I2C_SLAVE, addrB);
        // write(env.cBus, READ_CONF, 1);
        read(env.cBus, &(ret.cIn[sampleId * 2]), 2);
    }
    gettimeofday(&end, NULL);
    retRef->startTime =  start.tv_sec*1000LL + start.tv_usec/1000;
    retRef->endTime =  end.tv_sec*1000LL + end.tv_usec/1000;
    // printf("T: %lld\n", retRef->endTime-retRef->startTime);
}

PhData readIOGen(Common env, unsigned char addrA, unsigned char addrB) {
    unsigned char* rec_cIn =
        (unsigned char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    unsigned char* rec_cOut =
        (unsigned char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    unsigned char* rec_v =
        (unsigned char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    PhData ret = {rec_cIn, rec_cOut, rec_v};
    readIO(env, addrA, addrB, &ret);
    return ret;
}
void beFree(PhData data) {
    free(data.cIn);
    free(data.cOut);
    free(data.v);
}

int runIO(Common env) {
    char nullBuff[2] = {0};
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
    /* PhData ph2 = readIOGen(env, ADDR_CA, ADDR_CB);  // SWITCHED !!
    PhData ph1 = readIOGen(env, ADDR_CC, ADDR_CA);  // SWITCHED !!
    PhData ph3 = readIOGen(env, ADDR_CB, ADDR_CC); */
    PhData ph1 = readIOGen(env, ADDR_CA, ADDR_CB);
    PhData ph2 = readIOGen(env, ADDR_CB, ADDR_CC);
    PhData ph3 = readIOGen(env, ADDR_CC, ADDR_CA);
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
    // SET NIDE VALUE
    id_t pid = getpid();
    int ret = setpriority(PRIO_PROCESS, pid, -20);
    // printf("PID UID ret: %d %d %d\n", getpid(), getuid(), ret);


    Common env;
    env.cBus = open(I2C_FILE_C, O_RDWR);
    env.vBus = open(I2C_FILE_V, O_RDWR);
    env.outDesc = fopen(OUT_FILE, "w");

    int retCode = runIO(env);
    // printf("End with %d\n", retCode);

    close(env.cBus);
    close(env.vBus);
    fclose(env.outDesc);

    return retCode;
}
