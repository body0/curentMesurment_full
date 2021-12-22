#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <iostream>
#include <sstream>

#define SAMPLE_COUNT 300
#define ADDR_CA 0x4b
#define ADDR_CB 0x49
#define ADDR_CC 0x48
#define ADDR_V 0x48

#define I2C_FILE_C "/dev/i2c-1"
#define I2C_FILE_V "/dev/i2c-0"
#define OUT_FILE "/tmp/phase"
#define CONFIG_REG 0x01
#define READ_REG 0x00

const char VOLTAGE_CONFIG[] = {CONFIG_REG, 0x00, 0xA0};
const char CURENT_CONFIG_01[] = {CONFIG_REG, 0x08, 0xE3};
const char CURENT_CONFIG_23[] = {CONFIG_REG, 0x38, 0xE3};
const char NULL_CONFIG[] = {CONFIG_REG, 0x1, 0x83};
const char READ_CONF[] = {READ_REG};

typedef struct {
    FILE* outDesc;
    int cBus;
    int vBus;
} Common;

typedef struct {
    char* cIn;
    char* cOut;
    char* v;
} PhData;

void outputVal(Common env, int phId, PhData phaseList) {
    fprintf(env.outDesc, ">%d", phId);
    for (int sampleId = 0; sampleId < SAMPLE_COUNT; sampleId++) {
        int cIn = ((int)phaseList.cIn[sampleId * 2])
                  << 8 + (int)phaseList.cIn[sampleId * 2 + 1];
        int cOut = ((int)phaseList.cOut[sampleId * 2])
                   << 8 + (int)phaseList.cOut[sampleId * 2 + 1];
        int v = ((int)phaseList.v[sampleId * 2])
                << 8 + (int)phaseList.v[sampleId * 2 + 1];

        fprintf(env.outDesc, "=%d,%d,%d", cIn, cOut, v);
    }
}

void readIO(Common env, unsigned char addrA, unsigned char addrB, PhData ret) {
    ioctl(env.cBus, I2C_SLAVE, addrA);
    write(env.cBus, CURENT_CONFIG_01, 3);
    ioctl(env.cBus, I2C_SLAVE, addrB);
    write(env.cBus, CURENT_CONFIG_23, 3);

    for (int sampleId = 0; sampleId < SAMPLE_COUNT; sampleId++) {
        // read in
        ioctl(env.cBus, I2C_SLAVE, addrA);
        write(env.cBus, READ_REG, 1);
        read(env.cBus, &(ret.cIn[sampleId * 2]), 2);
        // read voltage
        write(env.vBus, READ_REG, 1);
        read(env.vBus, &(ret.v[sampleId * 2]), 2);
        // read out
        ioctl(env.cBus, I2C_SLAVE, addrB);
        write(env.cBus, READ_REG, 1);
        read(env.cBus, &(ret.cOut[sampleId * 2]), 2);
    }
}

PhData readIOGen(Common env, unsigned char addrA, unsigned char addrB) {
    char* rec_cIn = (char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    char* rec_cOut = (char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    char* rec_v = (char*)malloc(SAMPLE_COUNT * 2 * sizeof(char));
    PhData ret = {rec_cIn, rec_cOut, rec_v};
    readIO(env, ADDR_CA, ADDR_CB, ret);
    return ret;
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
    return 0;
    PhData ph1 = readIOGen(env, ADDR_CA, ADDR_CB);  // SWITCHED !!
    PhData ph2 = readIOGen(env, ADDR_CC, ADDR_CA);  // SWITCHED !!
    PhData ph3 = readIOGen(env, ADDR_CB, ADDR_CC);
    outputVal(env, 0, ph1);
    outputVal(env, 1, ph2);
    outputVal(env, 2, ph3);

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

void wrapIO() {
    Common env;
    env.cBus = open(I2C_FILE_C, O_RDWR);
    env.vBus = open(I2C_FILE_V, O_RDWR);
    env.outDesc = fopen(OUT_FILE, "w");

    int retCode = runIO(env);
    printf("End with %d\n", retCode);

    close(env.cBus);
    close(env.vBus);
    fclose(env.outDesc);
}

int main(int argc, char const* argv[]) {
    wrapIO();
    return 0;
}
