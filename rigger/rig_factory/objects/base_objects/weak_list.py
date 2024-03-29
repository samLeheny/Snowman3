import weakref


class WeakList(list):

    def __init__(self, seq=()):
        list.__init__(self)
        self._refs = []
        self._dirty = False
        for x in seq:
            self.append(x)


    def _mark_dirty(self, wref):
        self._dirty = True


    def flush(self):
        self._refs = [x for x in self._refs if x() is not None]
        self._dirty = False


    def __getitem__(self, index):
        if self._dirty:
            self.flush()
        return self._refs[index]()


    def __iter__(self):
        for ref in self._refs:
            obj = ref()
            if obj is not None: yield obj


    def __repr__(self):
        if len(self) > 0:
            return f'<WeakList{str(list(self))}s>'
        else:
            return '<WeakList[]> (Empty)'


    def __len__(self):
        if self._dirty: self.flush()
        return len(self._refs)


    def __setitem__(self, index, obj):
        if isinstance(index, slice):
            self._refs[index] = [weakref.ref(obj, self._mark_dirty) for _ in obj]
        else:
            self._refs[index] = weakref.ref(obj, self._mark_dirty)


    def __delitem__(self, index):
        del self._refs[index]


    def append(self, obj):
        self._refs.append(weakref.ref(obj, self._mark_dirty))

    def count(self, obj):
        return list(self).count(obj)

    def extend(self, items):
        for x in items: self.append(x)

    def index(self, obj):
        return list(self).index(obj)


    def insert(self, index, obj):
        self._refs.insert(index, weakref.ref(obj, self._mark_dirty))


    def pop(self, index):
        if self._dirty: self.flush()
        obj = self._refs[index]()
        del self._refs[index]
        return obj


    def remove(self, obj):
        if self._dirty: self.flush()  # Ensure all valid.
        for i, x in enumerate(self):
            if x == obj:
                del self[i]


    def reverse(self):
        self._refs.reverse()


    def sort(self, cmp=None, key=None, reverse=False):
        if self._dirty: self.flush()
        if key is not None:
            key = lambda x, key=key: key(x())
        else:
            key = apply
        self._refs.sort(cmp=cmp, key=key, reverse=reverse)


    def __add__(self, other):
        l = WeakList(self)
        l.extend(other)
        return l


    def __iadd__(self, other):
        self.extend(other)
        return self


    def __contains__(self, obj):
        return obj in list(self)


    def __mul__(self, n):
        return WeakList(list(self) * n)


    def __imul__(self, n):
        self._refs *= n
        return self


    def __getslice__(self, i, j):
        return WeakList(x() for x in self._refs[max(0, i):max(0, j):])


    def __setslice__(self, i, j, seq):
        self._refs[max(0, i):max(0, j):] = seq


    def __delslice__(self, i, j):
        del self._refs[max(0, i):max(0, j):]
