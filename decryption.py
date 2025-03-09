from ctypes import sizeof
from math import modf
from operator import xor
from PIL import Image
from pathlib import Path
import numpy
import sys

def findPrimePair(n, prime):
    for i in range(2, n):
        x = int(n / i)
        if prime[i] and prime[x] and x != i and x * i == n:
            return max(i, x)
    return n

def upshift(a, index, n):
    col = [a[j][index] for j in range(len(a))]
    shiftCol = numpy.roll(col, -n)
    for i in range(len(a)):
        if index < len(a[0]):
            a[i][index] = shiftCol[i]

def downshift(a, index, n):
    col = [a[j][index] for j in range(len(a))]
    shiftCol = numpy.roll(col, n)
    for i in range(len(a)):
        if index < len(a[0]):
            a[i][index] = shiftCol[i]

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

def main():
    # Get the image file name from command line argument
    if len(sys.argv) < 2:
        print("Please provide the image file name.")
        sys.exit(1)

    # Ensure directories exist
    Path("Input").mkdir(exist_ok=True)
    Path("Confusion").mkdir(exist_ok=True)
    Path("Encrypted").mkdir(exist_ok=True)
    Path("Decrypted").mkdir(exist_ok=True)

    image_name = sys.argv[1]
    encrypted_path = Path("Encrypted") / image_name
    decrypted_path = Path("Decrypted") / f"decrypted_{image_name}"

    # Check if encrypted file exists
    if not encrypted_path.exists():
        print(f"Error: File {encrypted_path} does not exist.")
        sys.exit(1)

    try:
        # Load the encrypted image
        im = Image.open(encrypted_path)
        pix = im.load()
        m, n = im.size
        M = m if m % 8 == 0 else 8 * (m // 8 + 1)
        N = n if n % 8 == 0 else 8 * (n // 8 + 1)
        blockSize = M * N // 64

        # Initialize RGB planes
        r, g, b = [], [], []
        for i in range(m):
            r.append([])
            g.append([])
            b.append([])
            for j in range(n):
                rgbPerPixel = pix[i, j]
                r[i].append(rgbPerPixel[0])
                g[i].append(rgbPerPixel[1])
                b[i].append(rgbPerPixel[2])

        # Check if keys.txt exists
        keys_path = Path('keys.txt')
        if not keys_path.exists():
            print("Error: keys.txt file not found. Please encrypt an image first.")
            sys.exit(1)

        # Read alpha and beta values from keys.txt
        with open('keys.txt', 'r') as f:
            alpha = int(f.readline())
            beta = int(f.readline())

        Q = 3 * M * N
        val = alpha / blockSize
        y = [modf(val)[0]]
        val = alpha / Q
        z = [modf(val)[0]]
        tempAlpha = alpha % blockSize
        
        # Use SieveOfEratosthenes function to generate prime array
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

        # Xor each RGB value with henonMap
        for i in range(m):
            for j in range(n):
                r[i][j] = xor(r[i][j], henonMap[(3 * i + j) % M])
                g[i][j] = xor(g[i][j], henonMap[(3 * i + j) % M])
                b[i][j] = xor(b[i][j], henonMap[(3 * i + j) % M])

        # Create shift vectors
        v1, v2 = [], []
        for i in range(M + N + 2):
            val = (y[i] * 10**14) % M
            v1.append(int(val))
            val = (z[i] * 10**14) % M
            v2.append(int(val))

        # Apply upshift/downshift transformations
        for i in range(n):
            rTotalSum = sum(r[j][i] for j in range(m))
            gTotalSum = sum(g[j][i] for j in range(m))
            bTotalSum = sum(b[j][i] for j in range(m))
            rModulus, gModulus, bModulus = rTotalSum % 2, gTotalSum % 2, bTotalSum % 2
            if rModulus == 0:
                downshift(r, i, v2[i])
            else:
                upshift(r, i, v2[i])
            if gModulus == 0:
                downshift(g, i, v2[i])
            else:
                upshift(g, i, v2[i])
            if bModulus == 0:
                downshift(b, i, v2[i])
            else:
                upshift(b, i, v2[i])

        # Apply horizontal shifts based on modulus
        for i in range(m):
            rTotalSum, gTotalSum, bTotalSum = sum(r[i]), sum(g[i]), sum(b[i])
            rModulus, gModulus, bModulus = rTotalSum % 2, gTotalSum % 2, bTotalSum % 2
            r[i] = numpy.roll(r[i], v1[i] if rModulus != 0 else -v1[i])
            g[i] = numpy.roll(g[i], v1[i] if gModulus != 0 else -v1[i])
            b[i] = numpy.roll(b[i], v1[i] if bModulus != 0 else -v1[i])

        # Update image pixels with decrypted RGB values
        for i in range(m):
            for j in range(n):
                pix[i, j] = (r[i][j], g[i][j], b[i][j])

        # Save decrypted image in Decrypted folder
        im.save(decrypted_path)
        print(f"Decrypted image saved at: {decrypted_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()