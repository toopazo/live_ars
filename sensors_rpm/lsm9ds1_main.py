from smbus import SMBus
# import LSM9DS1_I2C
import lsm9ds1


# LSB ADDRESS - configured by hardware - check your board
A = 1
sensorBus = SMBus(1)
# sensorInstance_A = lsm9ds1.LSM9DS1_I2C(sensorBus, A)

# lsm9ds1_A = lsm9ds1.LSM9DS1()
# sensorInstance_A = lsm9ds1.LSM9DS1_I2C(lsm9ds1_A)
sensorInstance_A = lsm9ds1.LSM9DS1_I2C(sensorBus)


accVal = sensorInstance_A.acceleration
gyroVal = sensorInstance_A.gyro
magVal = sensorInstance_A.magnetic

print(accVal, gyroVal, magVal)
