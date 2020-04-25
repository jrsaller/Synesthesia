import cv2
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

class DominantColorsClass:
    def __init__(self,image,clusters=3):
        self.mClusters = clusters
        self.mImage = image
        self.mKMax = 6

    def dominantColors(self):
        img = cv2.imread(self.mImage)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = img.reshape((img.shape[0]*img.shape[1],3))
        self.mImage = img
        kmeans = KMeans(n_clusters = self.mClusters)
        kmeans.fit(img)
        self.mColors = kmeans.cluster_centers_
        self.mLabels = kmeans.labels_
        return self.mColors.astype(int)

        