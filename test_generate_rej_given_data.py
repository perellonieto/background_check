import numpy
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
plt.ion()

from sklearn.decomposition import PCA

from cwc.synthetic_data import toy_examples
from cwc.synthetic_data import reject


def test_rej_data():
    samples = [500, 500]
    x, y = toy_examples.generate_gaussians(means=[[3,3,3],[5,5,5]],
                                  covs=[[[2,1,0],[1,1,0],[0,0,1]],
                                        [[1,0,0],[0,1,1],[0,1,2]]],
                                  samples=samples)
    fig = plt.figure('data')
    ax = fig.add_subplot(111, projection='3d')

    for k, c in [(0, 'r'), (1, 'b')]:
        index = (y == k)
        ax.scatter(x[index,0], x[index,1], x[index,2], c=c)

    pca = PCA(n_components=2, whiten=True)
    pca.fit(x)

    fig = plt.figure('pca')
    plt.clf()
    x_transform = pca.transform(x)
    for k, c in [(0, 'r'), (1, 'b')]:
        index = (y == k)
        plt.scatter(x_transform[index,0], x_transform[index,1], c=c)


    x_transform_means = x_transform.mean(axis=0)
    x_transform_std = x_transform.std(axis=0)

    radius=1
    r = reject.hypersphere_distribution(numpy.sum(samples),pca.n_components,
                                        radius=radius)
    # TODO compute the value of r before creating the hypersphere
    r *= numpy.sqrt(1.1/(numpy.mean(r**2)))

    plt.scatter(r[:,0], r[:,1], c='y')

    r_transform = pca.inverse_transform(r)

    ax.scatter(r_transform[:,0], r_transform[:,1], r_transform[:,2], c='y')

def test_rej_data_given_x():
    samples = [500, 500]
    x, y = toy_examples.generate_gaussians(means=[[3,3,3],[5,5,5]],
                                  covs=[[[2,1,0],[1,1,0],[0,0,1]],
                                        [[1,0,0],[0,1,1],[0,1,2]]],
                                  samples=samples)

    fig = plt.figure('data')
    ax = fig.add_subplot(111, projection='3d')
    for k, c in [(0, 'r'), (1, 'b')]:
        index = (y == k)
        ax.scatter(x[index,0], x[index,1], x[index,2], c=c)

    r = reject.create_reject_data(x, proportion=1, method='uniform_hsphere')
    ax.scatter(r[:,0], r[:,1], r[:,2], c='y')

if __name__ == '__main__':
    test_rej_data_given_x()
