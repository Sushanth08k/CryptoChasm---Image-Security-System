from ctypes import sizeof
from math import modf
from operator import xor
from PIL import Image
from random import randint
import numpy
import sys
from pathlib import Path

def assignPixels(plane, M, N):
    res = []
    for i in range(M):
        res.append([])
        for j in range(N):
            pixelValue = plane[i][j]
            binFormart = str(bin(pixelValue))[2:]
            count0 = binFormart.count('0')
            count1 = binFormart.count('1')
            if count0 > count1:
                res[i].append(0)
            else:
                res[i].append(1)
    return res

def decimalsInSubImages(plane, x, y):
    temp = []
    res = []
    for i in range(8):
        for j in range(8):
            temp.append(str(plane[8 * x + i][8 * y + j]))
    st = ''.join(temp)
    val = int(st, 2)
    res.append(val)
    return res

def SieveOfEratosthenes(n):
    prime = [True for i in range(n + 1)]
    p = 2
    while (p * p <= n):
        if (prime[p] == True):
            for i in range(p ** 2, n + 1, p):
                prime[i] = False
        p += 1
    prime[0] = False
    prime[1] = False
    return prime

def findPrimePair(n, prime):
    for i in range(2, n):
        x = int(n / i)
        if (prime[i] and prime[x] and x != i and x * i == n):
            return max(i, x)
    return n

def upshift(a, index, n):
    col = []
    for j in range(len(a)):
        col.append(a[j][index])
    shiftCol = numpy.roll(col, -n)
    for i in range(len(a)):
        for j in range(len(a[0])):
            if (j == index):
                a[i][j] = shiftCol[i]

def downshift(a, index, n):
    col = []
    for j in range(len(a)):
        col.append(a[j][index])
    shiftCol = numpy.roll(col, n)
    for i in range(len(a)):
        for j in range(len(a[0])):
            if (j == index):
                a[i][j] = shiftCol[i]

def main():
    # Accept file name from command line argument
    if len(sys.argv) < 2:
        print("Please provide an image filename as an argument.")
        sys.exit(1)

    file_name = sys.argv[1]
    if len(sys.argv) >= 3:
        beta = int(sys.argv[2])
    else:
        # Fallback to input if not provided as argument (for backward compatibility)
        beta = int(input("Enter the value of beta: "))
    input_path = Path("Input") / file_name
    confusion_path = Path("Confusion") / f"confusion_{file_name}"
    output_path = Path("Encrypted") / f"encrypted_{file_name}"


    
    # Ensure directories exist
    Path("Input").mkdir(exist_ok=True)
    Path("Confusion").mkdir(exist_ok=True)
    Path("Encrypted").mkdir(exist_ok=True)
    Path("Decrypted").mkdir(exist_ok=True)

    # Check if file exists
    if not input_path.exists():
        print(f"Error: File {input_path} does not exist.")
        sys.exit(1)

    try:
        # Open and process the image
        im = Image.open(input_path)
        pix = im.load()
        m = im.size[0]
        n = im.size[1]
        M = m if m % 8 == 0 else 8 * (m // 8 + 1)
        N = n if n % 8 == 0 else 8 * (n // 8 + 1)
        blockSize = M * N // 64

        r, R = [], []
        g, G = [], []
        b, B = [], []

        for i in range(m):
            r.append([])
            R.append([])
            g.append([])
            G.append([])
            b.append([])
            B.append([])
            for j in range(n):
                rgbPerPixel = pix[i, j]
                r[i].append(rgbPerPixel[0])
                R[i].append(rgbPerPixel[0])
                g[i].append(rgbPerPixel[1])
                G[i].append(rgbPerPixel[1])
                b[i].append(rgbPerPixel[2])
                B[i].append(rgbPerPixel[2])

        if m < M:
            for i in range(M - m):
                R.append([0] * N)
                G.append([0] * N)
                B.append([0] * N)

        if n < N:
            for i in range(m):
                for j in range(N - n):
                    R[i].append(0)
                    G[i].append(0)
                    B[i].append(0)

        R1 = assignPixels(R, M, N)
        G1 = assignPixels(G, M, N)
        B1 = assignPixels(B, M, N)

        avgs = []
        for i in range(M // 8):
            for j in range(N // 8):
                decimalNumbers_R = decimalsInSubImages(R1, i, j)
                decimalNumbers_G = decimalsInSubImages(G1, i, j)
                decimalNumbers_B = decimalsInSubImages(B1, i, j)
                sum_R = sum(decimalNumbers_R)
                sum_G = sum(decimalNumbers_G)
                sum_B = sum(decimalNumbers_B)
                sumOfBlock = sum_R + sum_G + sum_B
                avgs.append(sumOfBlock / 3)

        alpha = int(sum(avgs))
        
        # Get beta from user input
        beta = int(input("Enter the value of beta: "))

        # Write alpha and beta to keys.txt
        with open('keys.txt', 'w+') as f:
            f.write(f"{alpha}\n")
            f.write(f"{beta}\n")

        Q = 3 * M * N
        val = alpha / blockSize
        y = [modf(val)[0]]
        val = alpha / Q
        z = [modf(val)[0]]
        tempAlpha = alpha % blockSize
        prime = SieveOfEratosthenes(tempAlpha + beta * Q)
        val = findPrimePair(tempAlpha, prime) % 255
        henonMap = [val]

        for i in range(M + N + 2):
            tempAlpha += beta
            val = tempAlpha / blockSize
            y.append(modf(val)[0])
            val = tempAlpha / Q
            z.append(modf(val)[0])
            val = findPrimePair(tempAlpha, prime) % 255
            henonMap.append(val)

        v1 = []
        v2 = []
        for i in range(M + N + 2):
            val = (y[i] * 10**14) % M
            v1.append(int(val))
            val = (z[i] * 10**14) % M
            v2.append(int(val))

        # Perform confusion step
        for i in range(m):
            rTotalSum = sum(r[i])
            gTotalSum = sum(g[i])
            bTotalSum = sum(b[i])
            rModulus = rTotalSum % 2
            gModulus = gTotalSum % 2
            bModulus = bTotalSum % 2
            if rModulus == 0:
                r[i] = numpy.roll(r[i], v1[i])
            else:
                r[i] = numpy.roll(r[i], -v1[i])
            if gModulus == 0:
                g[i] = numpy.roll(g[i], v1[i])
            else:
                g[i] = numpy.roll(g[i], -v1[i])
            if bModulus == 0:
                b[i] = numpy.roll(b[i], v1[i])
            else:
                b[i] = numpy.roll(b[i], -v1[i])

        for i in range(n):
            rTotalSum = 0
            gTotalSum = 0
            bTotalSum = 0
            for j in range(m):
                rTotalSum += r[j][i]
                gTotalSum += g[j][i]
                bTotalSum += b[j][i]
            rModulus = rTotalSum % 2
            gModulus = gTotalSum % 2
            bModulus = bTotalSum % 2
            if rModulus == 0:
                upshift(r, i, v2[i])
            else:
                downshift(r, i, v2[i])
            if gModulus == 0:
                upshift(g, i, v2[i])
            else:
                downshift(g, i, v2[i])
            if bModulus == 0:
                upshift(b, i, v2[i])
            else:
                downshift(b, i, v2[i])

        # Save confusion image
        for i in range(m):
            for j in range(n):
                pix[i, j] = (r[i][j], g[i][j], b[i][j])

        im.save(confusion_path)
        print(f"Confusion image saved at {confusion_path}")

        # Perform diffusion step
        for i in range(m):
            for j in range(n):
                r[i][j] = xor(r[i][j], henonMap[(3 * i + j) % M])
                g[i][j] = xor(g[i][j], henonMap[(3 * i + j) % M])
                b[i][j] = xor(b[i][j], henonMap[(3 * i + j) % M])

        # Save encrypted image
        for i in range(m):
            for j in range(n):
                pix[i, j] = (r[i][j], g[i][j], b[i][j])

        im.save(output_path)
        print(f"Encrypted image saved at {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()