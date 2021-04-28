import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.signal import resample as fourier


def generiraj_ton_mono(cas, vzorcevalna_frekvenca, bitna_locljivost, frekvenca_tona):
    bres = ""
    if bitna_locljivost <= 8:
        bres = "int8"
    elif bitna_locljivost <= 16:
        bres = "int16"
    elif bitna_locljivost <= 32:
        bres = "int32"
    elif bitna_locljivost <= 64:
        bres = "int64"
    else:
        bres = ""
    Fvz = vzorcevalna_frekvenca
    f = frekvenca_tona
    T = cas
    amplituda = pow(2, bitna_locljivost) / 2 - 1
    generatedArray = (np.arange(0, Fvz * T, 1) / Fvz)
    generatedTone = (amplituda * np.sin(2 * np.pi * f * generatedArray))
    generatedTone = generatedTone.reshape(-1, 1).astype(bres)
    return generatedTone


def normaliziraj_vektorsko(vektor):
    return vektor / abs(vektor).max()


def dopler_efekt_mono(vektor, vektor_fvz, zacetna_oddaljenost, hitrost):
    reshapedVektor = vektor.reshape(-1, 1)
    size_of_vektor = reshapedVektor.size
    totalDistance = zacetna_oddaljenost * 2
    totalTime = totalDistance / hitrost
    size_sample = (vektor_fvz * totalTime)
    sound_speed = 343
#Rezanje do pravilne velikosti
    if size_of_vektor < size_sample:
        while size_sample > np.size(reshapedVektor):
            reshapedVektor = np.concatenate((reshapedVektor, reshapedVektor))
            # if size_of_vektor < size_sample:
            #    while size_sample > np.size(reshapedVektor):
            #       reshapedVektor = np.concatenate((reshapedVektor,reshapedVektor))
            #      if size_sample < np.size(reshapedVektor):
            #         reshapedVektor = reshapedVektor[0 : (int)(vektor_fvz * totalTime)]
            # elif size_of_vektor > size_sample:
            #   reshapedVektor = reshapedVektor[0 : (int)(vektor_fvz * totalTime)]
            # dela ampak čas prekoračen?
    # elif size_of_vektor > size_sample:


    reshapedVektor = normaliziraj_vektorsko(reshapedVektor[0: int(size_sample)])
    porazdeljenost_vzorcev = zacetna_oddaljenost / math.floor(reshapedVektor.size / 2)

#Sprememba jakosti
    #for x in np.nditer(reshapedVektor, op_flags=['readwrite']):
     #   x[...] = x * pow(i * porazdeljenost_vzorcev, 2)
     #   i += 1
    for x in range(math.floor(reshapedVektor.size / 2)):
        reshapedVektor[x] = reshapedVektor[x]* pow(x * porazdeljenost_vzorcev, 2)
    #i = 0
    #for x in np.nditer(reshapedVektor, op_flags=['readwrite']):
     #   x[...] = x * pow(i * porazdeljenost_vzorcev, 2)
    #    i += 1
    for j in range(math.floor(reshapedVektor.size / 2)):
        reshapedVektor[-j] = reshapedVektor[-j] * pow(j * porazdeljenost_vzorcev, 2)
#Sprememba frekvence
    split_reshaped_one = reshapedVektor[0: math.floor(reshapedVektor.size / 2)]
    split_reshape_two = reshapedVektor[math.floor(reshapedVektor.size / 2): reshapedVektor.size]
    #plt.plot(reshapedVektor)
    #plt.show()
    #upsampling / downsampling and the associated filtering, entirely in the frequency domain, using the Fourier Transform.
    #https://dsp.stackexchange.com/questions/45446/pythons-tt-resample-vs-tt-resample-poly-vs-tt-decimate
    newSample_near = int(reshapedVektor.size / (sound_speed / (sound_speed - hitrost)) / 2)
    newSample_far = int(reshapedVektor.size / (sound_speed / (sound_speed + hitrost)) / 2)
    firstHalf = fourier(split_reshaped_one, newSample_near).reshape(-1,1)
    secondHalf = fourier(split_reshape_two, newSample_far).reshape(-1,1)

    return normaliziraj_vektorsko(np.concatenate((firstHalf, secondHalf)).reshape(-1,1))


if __name__ == '__main__':
    import sounddevice as sd

    v = generiraj_ton_mono(2, 1000, 64, 200)
    v = dopler_efekt_mono(v, 1000, 40, 20)
    sd.play(v, 1000)
    sd.wait()
