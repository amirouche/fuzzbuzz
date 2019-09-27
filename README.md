# fuzzyhash

**experimental use at your own risks**

```ascii
  _____
_/ ____\_ _____________________.__.
\   __\  |  \___   /\___   <   |  |
 |  | |  |  //    /  /    / \___  |
 |__| |____//_____ \/_____ \/ ____|
                  \/      \/\/
.__                  .__
|  |__ _____    _____|  |__
|  |  \\__  \  /  ___/  |  \
|   Y  \/ __ \_\___ \|   Y  \
|___|  (____  /____  >___|  /
     \/     \/     \/     \/
```

fuzzy hash and distance for short strings.

```python
In [1]: import fuzzyhash

In [2]: fuzzyhash.hamming2(fuzzyhash.simhash('obama'), fuzzyhash.simhash('barack obama'))
Out[2]: 16

In [3]: fuzzyhash.hamming2(fuzzyhash.simhash('obama'), fuzzyhash.simhash('trump'))
Out[3]: 30

In [4]: fuzzyhash.hamming2(fuzzyhash.simhash('concept'), fuzzyhash.simhash('concpet'))
Out[4]: 22

In [5]: fuzzyhash.hamming2(fuzzyhash.simhash('concept'), fuzzyhash.simhash('concept'))
Out[5]: 0

In [6]: fuzzyhash.hamming2(fuzzyhash.simhash('concept'), fuzzyhash.simhash('concept car'))
Out[6]: 11

In [7]: fuzzyhash.hamming2(fuzzyhash.simhash('concept'), fuzzyhash.simhash('quality'))
Out[7]: 30

In [8]: fuzzyhash.hamming2(fuzzyhash.simhash('quality assurance'), fuzzyhash.simhash('quality'))
Out[8]: 17
```
