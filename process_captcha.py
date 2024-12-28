import pickle
import cv2
import numpy as np
import pandas as pd

class ProcessCaptcha:
    def __init__(self, filename, modelName):
        self.filename = filename
        self.modelName = modelName
        self.char_array = []
        self.threshold = 100

    def main(self):
        with open(f'assets/{self.modelName}.pkl', 'rb') as f:
            model = pickle.load(f)
        self.return_chars(self.threshold)
        captchaString = ""
        for char in self.char_array:
            pixel_array = []
            for a in char:
                for b in a:
                    pixel_array.append(b if b == 0 else 1)
            lis = pixel_array + [0 for _ in range(model.n_features_in_ - len(pixel_array))]
            pred_data = pd.DataFrame(data=[lis], columns=[f'pixel_{i+1}' for i in range(model.n_features_in_)])
            ch = chr(int(model.predict(pred_data)[0]))
            captchaString += ch
        return captchaString

    @staticmethod
    def detect_chars(image:np.ndarray):
        chars = []
        patterned = []
        def find_pattern(row:int, col:int) -> list[tuple[int, int]]:
            lis = []
            try:
                if image[row+1][col+1] != 0:
                    if (row+1, col+1) not in lis:
                        lis.append((row+1, col+1))
                    if (row+1, col+1) not in patterned:
                        patterned.append((row+1, col+1))
                        lis.extend(find_pattern(row+1, col+1))
            except:
                pass
            try:
                if image[row][col + 1] != 0:
                    if (row, col + 1) not in lis:
                        lis.append((row, col + 1))
                    if (row, col + 1) not in patterned:
                        patterned.append((row, col + 1))
                        lis.extend(find_pattern(row, col + 1))
            except:
                pass
            try:
                if image[row - 1][col + 1] != 0:
                    if (row - 1, col + 1) not in lis:
                        lis.append((row - 1, col + 1))
                    if (row - 1, col + 1) not in patterned:
                        patterned.append((row - 1, col + 1))
                        lis.extend(find_pattern(row - 1, col + 1))
            except:
                pass
            try:
                if image[row + 1][col] != 0:
                    if (row + 1, col) not in lis:
                        lis.append((row + 1, col))
                    if (row + 1, col) not in patterned:
                        patterned.append((row + 1, col))
                        lis.extend(find_pattern(row + 1, col))
            except:
                pass
            try:
                if image[row - 1][col] != 0:
                    if (row-1, col) not in lis:
                        lis.append((row-1, col))
                    if (row-1, col) not in patterned:
                        patterned.append((row-1, col))
                        lis.extend(find_pattern(row - 1, col))
            except:
                pass
            try:
                if image[row + 1][col - 1] != 0:
                    if (row+1, col-1) not in lis:
                        lis.append((row+1, col-1))
                    if (row+1, col-1) not in patterned:
                        patterned.append((row+1, col-1))
                        lis.extend(find_pattern(row + 1, col - 1))
            except:
                pass
            try:
                if image[row][col - 1] != 0:
                    if (row, col-1) not in lis:
                        lis.append((row, col-1))
                    if (row, col-1) not in patterned:
                        patterned.append((row, col-1))
                        lis.extend(find_pattern(row, col - 1))
            except:
                pass
            try:
                if image[row - 1][col - 1] != 0:
                    if (row-1, col-1) not in lis:
                        lis.append((row-1, col-1))
                    if (row-1, col-1) not in patterned:
                        patterned.append((row-1, col-1))
                        lis.extend(find_pattern(row - 1, col - 1))
            except:
                pass
            return lis

        for row_ind in range(len(image)):
            for col_ind in range(len(image[row_ind])):
                pixel = image[row_ind][col_ind]
                if pixel != 0:
                    state = False
                    for char in chars:
                        if (row_ind, col_ind) in char:
                            state = True
                            break
                    if not state:
                        chars.append(find_pattern(row_ind, col_ind))
        return chars

    def return_chars(self, thres, leftoff=0):
        try:
            image = cv2.imread(f'assets/{self.filename}.png')

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            _, thresh = cv2.threshold(gray, thres, 255, cv2.THRESH_BINARY_INV)

            chars = self.detect_chars(np.array(thresh))

            for i in range(leftoff, len(chars)):
                char = chars[i]
                x_min = np.min([char[a][1] for a in range(len(char))])
                y_min = np.min([char[b][0] for b in range(len(char))])
                x_minus = x_min - 2
                y_minus = y_min - 2
                new_ar = [(char[f][1] - x_minus, char[f][0] - y_minus) for f in range(len(char))]
                x_max = np.max([new_ar[c][0] for c in range(len(new_ar))])
                y_max = np.max([new_ar[d][1] for d in range(len(new_ar))])
                img = [[0 for _ in range(x_max + 3)] for _ in range(y_max + 3)]
                for w in range(x_max + 3):
                    for h in range(y_max + 3):
                        if (w, h) in new_ar:
                            img[h][w] = 1
                if len(img[0]) > 30:
                    self.return_chars(thres-1, i)
                    return None
                elif len(img[0]) < 14 or len(img) < 10:
                    continue
                la = []
                for a in img:
                    l = []
                    for b in a:
                        l.append(b if b == 0 else 255)
                    la.append(l)
                self.char_array.append(np.array(img))
        except ValueError:
            pass