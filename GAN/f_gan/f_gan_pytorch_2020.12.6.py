import torch
import torch.nn
import torch.nn.functional as nn
import torch.autograd as autograd
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
from torch.autograd import Variable
from tensorflow.examples.tutorials.mnist import input_data
# from tensorflow_core.examples.tutorials.mnist import input_data
#No module named 'tensorflow.examples
#https://blog.csdn.net/weixin_42515907/article/details/105102978

mnist = input_data.read_data_sets('../../MNIST_data', one_hot=True)
#放数据集的坑
#https://blog.csdn.net/wuzhichenggo/article/details/79332128
mb_size = 32
z_dim = 10
X_dim = mnist.train.images.shape[1]
y_dim = mnist.train.labels.shape[1]
h_dim = 128
cnt = 0
lr = 1e-3


def log(x):
    return torch.log(x + 1e-8)


G = torch.nn.Sequential(
    torch.nn.Linear(z_dim, h_dim),
    torch.nn.ReLU(),
    torch.nn.Linear(h_dim, X_dim),
    torch.nn.Sigmoid()
)


D = torch.nn.Sequential(
    torch.nn.Linear(X_dim, h_dim),
    torch.nn.ReLU(),
    torch.nn.Linear(h_dim, 1),
)


def reset_grad():
    G.zero_grad()
    D.zero_grad()


G_solver = optim.Adam(G.parameters(), lr=lr)
D_solver = optim.Adam(D.parameters(), lr=lr)


for it in range(1000000):
    # Sample data
    z = Variable(torch.randn(mb_size, z_dim))
    X, _ = mnist.train.next_batch(mb_size)
    X = Variable(torch.from_numpy(X))

    # Dicriminator
    G_sample = G(z)
    D_real = D(X)
    D_fake = D(G_sample)

    # Uncomment D_loss and its respective G_loss of your choice
    # ---------------------------------------------------------

    """ Total Variation """
    # D_loss = -(torch.mean(0.5 * torch.tanh(D_real)) -
    #            torch.mean(0.5 * torch.tanh(D_fake)))
    """ Forward KL """
    # D_loss = -(torch.mean(D_real) - torch.mean(torch.exp(D_fake - 1)))
    """ Reverse KL """
    D_loss = -(torch.mean(-torch.exp(D_real)) - torch.mean(-1 - D_fake))
    """ Pearson Chi-squared """
    # D_loss = -(torch.mean(D_real) - torch.mean(0.25*D_fake**2 + D_fake))
    """ Squared Hellinger """
    # D_loss = -(torch.mean(1 - torch.exp(D_real)) -
    #            torch.mean((1 - torch.exp(D_fake)) / (torch.exp(D_fake))))

    D_loss.backward()
    D_solver.step()
    reset_grad()

    # Generator
    G_sample = G(z)
    D_fake = D(G_sample)

    """ Total Variation """
    # G_loss = -torch.mean(0.5 * torch.tanh(D_fake))
    """ Forward KL """
    # G_loss = -torch.mean(torch.exp(D_fake - 1))
    """ Reverse KL """
    G_loss = -torch.mean(-1 - D_fake)
    """ Pearson Chi-squared """
    # G_loss = -torch.mean(0.25*D_fake**2 + D_fake)
    """ Squared Hellinger """
    # G_loss = -torch.mean((1 - torch.exp(D_fake)) / (torch.exp(D_fake)))

    G_loss.backward()
    G_solver.step()
    reset_grad()

    # Print and plot every now and then
    # if it % 1000 == 0:
    #     print('Iter-{}; D_loss: {:.4}; G_loss: {:.4}'
    #           .format(it, D_loss.data[0], G_loss.data[0]))
    if it % 1000 == 0:
        print('Iter-{}; D_loss: {:.4}; G_loss: {:.4}'
              .format(it, D_loss.item(), G_loss.item()))
#IndexError: invalid index of a 0-dim tensor. Use `tensor.item()` in Python or `tensor.item<T>()` in C++ to convert a 0-dim tensor to a number
#https://blog.csdn.net/severe777777/article/details/97762401
        samples = G(z).data.numpy()[:16]

        fig = plt.figure(figsize=(4, 4))
        gs = gridspec.GridSpec(4, 4)
        gs.update(wspace=0.05, hspace=0.05)

        for i, sample in enumerate(samples):
            ax = plt.subplot(gs[i])
            plt.axis('off')
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_aspect('equal')
            plt.imshow(sample.reshape(28, 28), cmap='Greys_r')

        if not os.path.exists('out/'):
            os.makedirs('out/')

        plt.savefig('out/{}.png'.format(str(cnt).zfill(3)), bbox_inches='tight')
        cnt += 1
        plt.close(fig)
