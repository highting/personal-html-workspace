# LeetCode Hot100 学习资料

按[官方 Hot100](https://leetcode.cn/studyplan/top-100-liked/)的 17 个分类、100 题顺序整理。题面为忠实转述；200 份 Python 实现依据各题所链接的灵茶山艾府题解整理，每种做法附思路、复杂度和必要提醒。

每个代码块都是独立版本，提交时完整复制其中一个。节点类型由 LeetCode 提供。树的列表示例按层序表示，`null` 表示空孩子；箭头表示节点连接。复杂度默认不计返回结果，特别说明的除外。

## 分类目录

- [哈希](#哈希)：3 题
- [双指针](#双指针)：4 题
- [滑动窗口](#滑动窗口)：2 题
- [子串](#子串)：3 题
- [普通数组](#普通数组)：5 题
- [矩阵](#矩阵)：4 题
- [链表](#链表)：14 题
- [二叉树](#二叉树)：15 题
- [图论](#图论)：4 题
- [回溯](#回溯)：8 题
- [二分查找](#二分查找)：6 题
- [栈](#栈)：5 题
- [堆](#堆)：3 题
- [贪心算法](#贪心算法)：4 题
- [动态规划](#动态规划)：10 题
- [多维动态规划](#多维动态规划)：5 题
- [技巧](#技巧)：5 题

## 哈希

### 两数之和（LeetCode 1）

简单 · [力扣原题](https://leetcode.cn/problems/two-sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/two-sum/solutions/2326193/dong-hua-cong-liang-shu-zhi-he-zhong-wo-0yvmj/)

#### 题面

给定整数数组 `nums` 和整数 `target`，从数组中选出两个不同位置，使这两个位置上的数相加等于 `target`。返回这两个位置的下标。

同一个位置不能使用两次。题目保证只有一组符合条件的答案，返回两个下标的顺序不限。

**数据范围与约定**

- `2 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
- 只会存在一个有效答案

**进阶要求**

- 你可以想出一个时间复杂度小于 \(O(n^2)\) 的算法吗？

**示例**

`nums=[4,9,2]`、`target=11`，返回 `[1,2]`，因为 `nums[1]+nums[2]=9+2=11`。

#### 解法：哈希表找另一个数

从左到右扫描，用字典记录已经出现的数及其下标。当前数为 `value` 时，查询 `target - value` 是否已经出现；找到就返回两个下标，否则记录当前数。先查再记，保证不会使用同一个位置两次。

```python
class Solution:

    def twoSum(self, nums, target):
        seen = {}
        for i, value in enumerate(nums):
            other = target - value
            if other in seen:
                return [seen[other], i]
            seen[value] = i
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)；\(n\) 为数组长度。

#### 补充：枚举两个下标

固定第一个下标，只检查它右边的元素，找到和为目标值的一对便返回。这样不会重复使用同一位置，也不会把同一对下标检查两遍。

```python
class Solution:
    def twoSum(self, nums, target):
        for first in range(len(nums)):
            for second in range(first + 1, len(nums)):
                if nums[first] + nums[second] == target:
                    return [first, second]
```

**复杂度：** 时间 \(O(n^2)\)，额外空间 \(O(1)\)。

**注意：** 用于理解最直接的做法，大输入可能超时。

### 字母异位词分组（LeetCode 49）

中等 · [力扣原题](https://leetcode.cn/problems/group-anagrams/) · [灵茶山艾府题解](https://leetcode.cn/problems/group-anagrams/solutions/2718519/ha-xi-biao-fen-zu-jian-ji-xie-fa-pythonj-1ukv/)

#### 题面

给定字符串数组 `strs`，把字母组成相同的字符串分到同一组，返回分组后的二维列表。这里的“组成相同”是指每种字母及其出现次数都相同，字母排列顺序可以不同。

例如 `ab` 和 `ba` 应分到同组，`ab` 和 `aab` 则不能。各组之间、每组内部的排列顺序都不影响答案。

**数据范围与约定**

- `1 <= strs.length <= 10^4`
- `0 <= strs[i].length <= 100`
- `strs[i] 仅包含小写字母`

**示例**

`["ab","ba","aab","aba","c"]` 可分为 `[["ab","ba"],["aab","aba"],["c"]]`。每组字符串的字母及出现次数相同。

#### 解法：按排序结果分组

把每个字符串的字母排序，用排序结果作为字典的键。字母种类和数量相同的字符串，排序结果一定相同，因此会进入同一组。最后返回所有分组。

```python
class Solution:

    def groupAnagrams(self, strs):
        groups = {}
        for text in strs:
            key = ''.join(sorted(text))
            groups.setdefault(key, []).append(text)
        return list(groups.values())
```

**复杂度：** 时间 \(O(nm\log m)\)，空间 \(O(nm)\)，含分组结果；\(n\) 为字符串个数，\(m\) 为最大字符串长度。

**写法补充：** 原文的普通字典与 `defaultdict` 写法使用同样的排序分组方法。

### 最长连续序列（LeetCode 128）

中等 · [力扣原题](https://leetcode.cn/problems/longest-consecutive-sequence/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-consecutive-sequence/solutions/3005726/ha-xi-biao-on-zuo-fa-pythonjavacgojsrust-whop/)

#### 题面

给定未排序的整数数组 `nums`，找出其中能组成的最长连续整数序列，并返回序列长度。连续是指数值依次相差一，例如 3、4、5、6。

这些数不必在原数组中相邻，也不必原本按顺序出现；重复值不会增加序列长度。要求时间复杂度为 \(O(n)\)，其中 \(n\) 是数组长度。

**数据范围与约定**

- `0 <= nums.length <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

**示例**

`[8,2,5,3,4,2]` 返回 `4`，最长连续整数是 `2,3,4,5`；重复的 `2` 不增加长度。

#### 解法：只从连续段的起点向后找

先用集合去重。对数值 `x`，只有 `x-1` 不在集合中时，才从它开始依次查找 `x+1`、`x+2`。这样每段连续整数只扫描一次，取最长段即可。

```python
class Solution:

    def longestConsecutive(self, nums):
        values = set(nums)
        best = 0
        for start in values:
            if start - 1 in values:
                continue
            end = start
            while end in values:
                end += 1
            best = max(best, end - start)
        return best
```

**复杂度：** 平均时间 \(O(n)\)，空间 \(O(u)\)；\(n\) 为数组长度，\(u\) 为不同元素个数。

**写法补充：** 原文另有提前结束的优化：一段的长度达到去重后元素数的一半时即可停止，因为其余所有段合起来也不可能更长。


## 双指针

### 移动零（LeetCode 283）

简单 · [力扣原题](https://leetcode.cn/problems/move-zeroes/) · [灵茶山艾府题解](https://leetcode.cn/problems/move-zeroes/solutions/2969353/kuai-man-zhi-zhen-wei-shi-yao-ke-yi-ba-s-1h8x/)

#### 题面

给定整数数组 `nums`，把所有零移动到数组末尾，同时保持其他元素原来的先后顺序。

直接修改输入数组，不要创建另一个完整数组来代替它。函数不需要返回新数组；例如 `[0,5,0,2]` 应变成 `[5,2,0,0]`。

**数据范围与约定**

- `1 <= nums.length <= 10^4`
- `-2^31 <= nums[i] <= 2^31 - 1`

**进阶要求**

- 你能尽量减少完成的操作次数吗？

**示例**

`[0,5,0,2,7]` 改为 `[5,2,7,0,0]`，非零元素仍按 `5、2、7` 的顺序排列。

#### 解法：双指针交换非零元素

一个指针扫描数组，另一个指向下一个非零元素应放的位置。遇到非零元素，就把它交换到该位置，并推进写入指针。非零元素按原顺序放到前面，零自然留在后面。

```python
class Solution:

    def moveZeroes(self, nums):
        write = 0
        for read in range(len(nums)):
            if nums[read] != 0:
                nums[write], nums[read] = (nums[read], nums[write])
                write += 1
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

#### 补充：先写非零元素，再补零

用 `write` 表示下一个非零元素应写入的位置。扫描时只把非零元素依次放到前面；扫描结束后，剩下的位置统一填零。`write` 不会超过当前读取位置，因此不会覆盖尚未读取的数据。

```python
class Solution:
    def moveZeroes(self, nums):
        write = 0
        for value in nums:
            if value != 0:
                nums[write] = value
                write += 1
        for pos in range(write, len(nums)):
            nums[pos] = 0
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 与交换法效率相同；先写非零元素，再单独补零。

**写法补充：** 另一写法用切片一次补零，但会创建临时零列表；这里逐项补零，只需常数额外空间。

### 盛最多水的容器（LeetCode 11）

中等 · [力扣原题](https://leetcode.cn/problems/container-with-most-water/) · [灵茶山艾府题解](https://leetcode.cn/problems/container-with-most-water/solutions/1974355/by-endlesscheng-f0xz/)

#### 题面

给定非负整数数组 `height`，下标 `i` 处竖着一条高度为 `height[i]` 的线。选择其中两条线，与横轴一起形成一个盛水容器，返回能盛下的最大水量。

两条线之间的距离是容器宽度，较短那条线的高度决定水位，因此容量等于距离乘较短高度。容器不能倾斜，必须选择两个不同下标。

**数据范围与约定**

- `n == height.length`
- `2 <= n <= 10^5`
- `0 <= height[i] <= 10^4`

**示例**

`[2,7,4,6]` 返回 `12`：选择下标 `1` 和 `3`，宽度为 `2`，水位为 `6`。

#### 解法：双指针，每次移动较短边

两指针从数组两端出发，先计算当前容量，再向内移动较短的一边。因为固定短边、只移动长边，宽度会变小，水位也无法超过短边，容量不会更大；所以短边可以安全排除。

```python
class Solution:

    def maxArea(self, height):
        left, right = (0, len(height) - 1)
        best = 0
        while left < right:
            best = max(best, (right - left) * min(height[left], height[right]))
            if height[left] <= height[right]:
                left += 1
            else:
                right -= 1
        return best
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为高度数组长度。

### 三数之和（LeetCode 15）

中等 · [力扣原题](https://leetcode.cn/problems/3sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/3sum/solutions/1968332/shuang-zhi-zhen-xiang-bu-ming-bai-yi-ge-pno55/)

#### 题面

给定整数数组 `nums`，找出所有由三个不同位置组成、数值之和等于零的组合。返回这些组合中的三个数，而不是它们的下标。

一个位置只能使用一次，但不同位置可以有相同数值。相同的数值组合只返回一次；例如 `[-1,0,1]` 与 `[1,-1,0]` 算同一个答案。结果顺序不限。

**数据范围与约定**

- `3 <= nums.length <= 3000`
- `-10^5 <= nums[i] <= 10^5`

**示例**

`[-3,-1,0,1,2,3]` 返回 `[[-3,0,3],[-3,1,2],[-1,0,1]]`；每组三数之和为零，且没有重复组合。

#### 解法：排序后固定一个数，用双指针找另外两个

先排序，固定第一个数，再在右侧用双指针找和为它相反数的一对：总和小于零就左指针右移，大于零就右指针左移。找到后跳过重复值，固定的第一个数也要去重。

搜索前先检查：当前数加后面最小两数已大于零，可以结束；加最大两数仍小于零，则跳过当前数。

```python
class Solution:

    def threeSum(self, nums):
        nums.sort()
        answer = []
        size = len(nums)
        for i in range(size - 2):
            first = nums[i]
            if i and first == nums[i - 1]:
                continue
            if first + nums[i + 1] + nums[i + 2] > 0:
                break
            if first + nums[-2] + nums[-1] < 0:
                continue
            left, right = (i + 1, size - 1)
            while left < right:
                total = first + nums[left] + nums[right]
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    answer.append([first, nums[left], nums[right]])
                    left += 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1
                    right -= 1
                    while right > left and nums[right] == nums[right + 1]:
                        right -= 1
        return answer
```

**复杂度：** 时间 \(O(n^2)\)，Python 排序最坏需 \(O(n)\) 辅助空间；不计结果。

**注意：** 会原地排序输入数组。

**写法补充：** 原文的另一版本调整了跳过重复值的位置，算法相同。

### 接雨水（LeetCode 42）

困难 · [力扣原题](https://leetcode.cn/problems/trapping-rain-water/) · [灵茶山艾府题解](https://leetcode.cn/problems/trapping-rain-water/solutions/1974340/zuo-liao-nbian-huan-bu-hui-yi-ge-shi-pin-ukwm/)

#### 题面

给定非负整数数组 `height`，把每个元素看作一根宽度为一、对应高度的柱子。这些柱子从左到右紧挨着排列。下雨后，低处可能被左右较高的柱子围住而积水，求总积水量。

柱子占据的部分不能存水，雨水可以从整个排列的左右两端流走。返回所有位置积水量之和。

**数据范围与约定**

- `n == height.length`
- `1 <= n <= 2 * 10^4`
- `0 <= height[i] <= 10^5`

**示例**

`[3,0,2,0,4]` 返回 `7`，中间三处分别积水 `3、1、3`。

#### 解法：双指针维护两侧最高柱子

`left_max`、`right_max` 分别记录从两端扫描到的最高柱子。若 `left_max <= right_max`，右边已有足够高的挡板，左端位置可存的水就是 `left_max - height[left]`，算完后左指针右移。反之计算右端，直到所有位置处理完。

```python
class Solution:

    def trap(self, height):
        left, right = (0, len(height) - 1)
        left_max = right_max = answer = 0
        while left <= right:
            left_max = max(left_max, height[left])
            right_max = max(right_max, height[right])
            if left_max <= right_max:
                answer += left_max - height[left]
                left += 1
            else:
                answer += right_max - height[right]
                right -= 1
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为柱子个数。

#### 补充：分别记录左右最高柱子

每个位置的水面不能高于左右两侧最高柱子中较矮的一根。先分别从左向右、从右向左记录最高高度，再把水面减去当前柱高，累加每个位置的水量。

```python
class Solution:
    def trap(self, height):
        size = len(height)
        left_high = height.copy()
        right_high = height.copy()
        for pos in range(1, size):
            left_high[pos] = max(left_high[pos - 1], height[pos])
        for pos in range(size - 2, -1, -1):
            right_high[pos] = max(right_high[pos + 1], height[pos])
        return sum(min(left_high[pos], right_high[pos]) - height[pos]
                   for pos in range(size))
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)。

**注意：** 左右信息显式保存在数组中，直观，但比双指针法多用线性空间。

#### 补充：单调栈，按水层计算

栈保存尚未找到右侧挡板的位置，柱高从栈底到栈顶递减。遇到更高或等高柱子时，弹出的柱子是这一层水的底，新的栈顶是左挡板，当前柱子是右挡板。层高取两块挡板中较矮者减去底高，宽度是两块挡板之间的位置数。

```python
class Solution:
    def trap(self, height):
        pending = []
        water = 0
        for right, right_height in enumerate(height):
            while pending and height[pending[-1]] <= right_height:
                bottom = pending.pop()
                if not pending:
                    break
                left = pending[-1]
                layer = min(height[left], right_height) - height[bottom]
                water += layer * (right - left - 1)
            pending.append(right)
        return water
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)。

**注意：** 每个下标至多入栈、出栈一次，所以总时间是线性的。


## 滑动窗口

### 无重复字符的最长子串（LeetCode 3）

中等 · [力扣原题](https://leetcode.cn/problems/longest-substring-without-repeating-characters/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-substring-without-repeating-characters/solutions/1959540/xia-biao-zong-suan-cuo-qing-kan-zhe-by-e-iaks/)

#### 题面

给定字符串 `s`，找出其中最长的一段连续字符，使这一段里没有任何字符重复，返回它的长度。

必须选连续的一段，不能跳过中间字符拼接。只返回长度；如果 `s` 为空，返回 0。大小写、数字、空格和其他符号都按各自字符处理。

**数据范围与约定**

- `0 <= s.length <= 10^5`
- `s` 由英文字母、数字、符号和空格组成

**示例**

`s="abcaef"` 返回 `5`，最长无重复子串为 `"bcaef"`。

#### 解法：用字符计数维护无重复窗口

左右指针之间就是当前子串。右端每加入一个字符，增加它的计数；如果重复，就不断移出左端字符，直到新字符只剩一次。此时窗口是以当前右端结尾的最长合法子串，用它的长度更新答案。

```python
class Solution:

    def lengthOfLongestSubstring(self, s):
        counts = {}
        left = best = 0
        for right, char in enumerate(s):
            counts[char] = counts.get(char, 0) + 1
            while counts[char] > 1:
                old = s[left]
                counts[old] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(|\Sigma|)\)；\(n\) 为字符串长度，\(\Sigma\) 为字符集。

#### 补充：集合维护无重复窗口

集合记录当前窗口已有的字符。准备加入右端字符时，若集合已经有它，就不断移出左端字符，直到旧的同名字符离开。此时加入新字符，窗口仍无重复，可用其长度更新答案。

```python
class Solution:
    def lengthOfLongestSubstring(self, s):
        present = set()
        start = best = 0
        for end, char in enumerate(s):
            while char in present:
                present.remove(s[start])
                start += 1
            present.add(char)
            best = max(best, end - start + 1)
        return best
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(\min(n, \text{字符集大小}))\)。

### 找到字符串中所有字母异位词（LeetCode 438）

中等 · [力扣原题](https://leetcode.cn/problems/find-all-anagrams-in-a-string/) · [灵茶山艾府题解](https://leetcode.cn/problems/find-all-anagrams-in-a-string/solutions/2969498/liang-chong-fang-fa-ding-chang-hua-chuan-14pd/)

#### 题面

给定字符串 `s` 和 `p`，在 `s` 中寻找所有长度等于 `p`、字母出现次数也与 `p` 完全相同的连续子串。返回这些子串的起始下标。

子串内字母的顺序可以不同，例如 `ab` 与 `ba` 符合条件。一个字母出现几次也必须一致；各答案窗口可以相互重叠，返回下标的顺序不限。

**数据范围与约定**

- `1 <= s.length, p.length <= 3 * 10^4`
- `s` 和 `p` 仅包含小写字母

**示例**

`s="baba"`、`p="ab"`，返回 `[0,1,2]`，对应子串为 `"ba"、"ab"、"ba"`。

#### 解法：维护每种字符都不超额的窗口

先统计 `p` 的字符数量，把它看作每种字符的可用额度。加入字符时减一；额度变负，就从左侧移出字符并归还额度，直到恢复。此前其他字符都没有超额，所以只需检查新加入的字符。

窗口没有超额且长度等于 `p` 时，每种字符的数量必然恰好相同，记录左端下标。

```python
from collections import Counter

class Solution:

    def findAnagrams(self, s, p):
        remaining = Counter(p)
        answer = []
        left = 0
        for right, char in enumerate(s):
            remaining[char] -= 1
            while remaining[char] < 0:
                remaining[s[left]] += 1
                left += 1
            if right - left + 1 == len(p):
                answer.append(left)
        return answer
```

**复杂度：** 时间 \(O(n+m)\)，辅助空间 \(O(26)\)；\(n,m\) 分别为 \(s,p\) 的长度。

#### 补充：固定长度窗口比较字符计数

窗口长度固定为 `p` 的长度。右端加入一个字符，窗口凑满后比较两份字符计数；相同便记录左端下标。然后移出左端字符，为下一轮腾出一个位置。

```python
from collections import Counter

class Solution:
    def findAnagrams(self, s, p):
        needed = Counter(p)
        current = Counter()
        answer = []
        width = len(p)
        for end, char in enumerate(s):
            current[char] += 1
            begin = end + 1 - width
            if begin >= 0:
                if current == needed:
                    answer.append(begin)
                current[s[begin]] -= 1
        return answer
```

**复杂度：** 时间 \(O(n\Sigma+m)\)，空间 \(O(\Sigma)\)；n、m 分别为 s、p 的长度，Σ=26。

**注意：** `Counter` 比较字符次数时，零计数与缺失键按相同处理。


## 子串

### 和为 K 的子数组（LeetCode 560）

中等 · [力扣原题](https://leetcode.cn/problems/subarray-sum-equals-k/) · [灵茶山艾府题解](https://leetcode.cn/problems/subarray-sum-equals-k/solutions/2781031/qian-zhui-he-ha-xi-biao-cong-liang-ci-bi-4mwr/)

#### 题面

给定整数数组 `nums` 和整数 `k`，统计有多少个非空连续子数组的元素和恰好等于 `k`，返回数量。

子数组必须由原数组中相邻的元素组成。不同起止位置分别计数，即使数值内容相同也算不同子数组。数组中可能有零和负数。

**数据范围与约定**

- `1 <= nums.length <= 2 * 10^4`
- `-1000 <= nums[i] <= 1000`
- `-10^7 <= k <= 10^7`

**示例**

`nums=[2,-1,2]`、`k=2`，返回 `2`，两个单独的 `2` 各构成一个答案。

#### 解法：前缀和加计数字典

`prefix` 是从开头到当前位置的累计和。若此前累计和 `prefix-k` 出现过若干次，就有同样多的子数组以当前位置结尾、和为 `k`。用字典累计这些次数；先查询再记录当前和，避免计入空子数组。初始记一次累计和 `0`，用于处理从数组开头起的答案。

```python
class Solution:

    def subarraySum(self, nums, k):
        counts = {0: 1}
        prefix = answer = 0
        for value in nums:
            prefix += value
            answer += counts.get(prefix - k, 0)
            counts[prefix] = counts.get(prefix, 0) + 1
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)；\(n\) 为数组长度。

#### 补充：先存完整前缀和，再统计配对

`prefix[j]` 是前 j 个数的和。以 j 为右边界的目标子数组，对应先前出现过的 `prefix[j]`−`k`。依次扫描所有前缀和，先查询再登记当前值，确保子数组非空。

```python
from collections import defaultdict

class Solution:
    def subarraySum(self, nums, k):
        prefix = [0]
        for value in nums:
            prefix.append(prefix[-1] + value)
        seen = defaultdict(int)
        total = 0
        for value in prefix:
            total += seen[value - k]
            seen[value] += 1
        return total
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)。

**注意：** 与主解法的统计原理相同；这里保留前缀和数组，展示由公式到实现的两步过程。

**写法补充：** 一次遍历另有空前缀登记时机不同的等价写法。

### 滑动窗口最大值（LeetCode 239）

困难 · [力扣原题](https://leetcode.cn/problems/sliding-window-maximum/) · [灵茶山艾府题解](https://leetcode.cn/problems/sliding-window-maximum/solutions/2499715/shi-pin-yi-ge-shi-pin-miao-dong-dan-diao-ezj6/)

#### 题面

给定数组 `nums` 和窗口长度 `k`。从最左边的 `k` 个连续元素开始，每次把窗口向右移动一个位置，直到窗口到达数组末尾。返回每个窗口中的最大值。

结果按窗口从左到右出现的顺序排列，共有 `len(nums)-k+1` 项。窗口长度始终是 `k`，且题目保证 `k` 有效。

**数据范围与约定**

- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `1 <= k <= nums.length`

**示例**

`nums=[4,1,3,2]`、`k=2`，三个窗口是 `[4,1]、[1,3]、[3,2]`，返回 `[4,3,3]`。

#### 解法：用双端队列保存最大值候选

队列存下标，对应数值从大到小排列。加入新值时，删除队尾不大于它的候选：新值更大或相等，而且更晚离开窗口，这些旧值不再有用。再移除队首已经离开窗口的下标；窗口凑满后，队首就是最大值。

```python
from collections import deque

class Solution:

    def maxSlidingWindow(self, nums, k):
        candidates = deque()
        answer = []
        for i, value in enumerate(nums):
            while candidates and nums[candidates[-1]] <= value:
                candidates.pop()
            candidates.append(i)
            if candidates[0] <= i - k:
                candidates.popleft()
            if i >= k - 1:
                answer.append(nums[candidates[0]])
        return answer
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(k)\)，输出另计；\(n\) 为数组长度，\(k\) 为窗口大小。

### 最小覆盖子串（LeetCode 76）

困难 · [力扣原题](https://leetcode.cn/problems/minimum-window-substring/) · [灵茶山艾府题解](https://leetcode.cn/problems/minimum-window-substring/solutions/2713911/liang-chong-fang-fa-cong-o52mn-dao-omnfu-3ezz/)

#### 题面

给定字符串 `s` 和 `t`，在 `s` 中找出最短的连续子串，使它包含 `t` 中的全部字符，返回这个子串；找不到时返回空字符串。

如果某字符在 `t` 中出现多次，所选子串中也至少要出现相应次数。字符顺序不必与 `t` 相同，大小写视为不同字符；有解时题目保证最短答案唯一。

**数据范围与约定**

- `m == s.length`
- `n == t.length`
- `1 <= m, n <= 10^5`
- `s` 和 `t` 由英文字母组成

**进阶要求**

- 你能设计一个在 \(O(m + n)\) 时间内解决此问题的算法吗？

**示例**

`s="aabcbc"`、`t="abc"`，返回 `"abc"`；它包含所需的三个字符，且不能再缩短。

#### 解法：先扩大到覆盖，再尽量缩小

`missing` 记录各字符还缺几个，`satisfied` 记录已有多少种字符够用。右端加入字符，某种字符从缺一个变为不缺时，满足种数加一。

所有种类都够用后，记录答案并不断移出左端字符；一旦某种字符重新不足，就停止缩小，继续扩展右端。这样能找到每个右端对应的最短覆盖。

```python
from collections import Counter

class Solution:

    def minWindow(self, s, t):
        if not t:
            return ''
        missing = Counter(t)
        satisfied = left = 0
        best_start, best_length = (0, len(s) + 1)
        for right, char in enumerate(s):
            if char in missing:
                missing[char] -= 1
                if missing[char] == 0:
                    satisfied += 1
            while satisfied == len(missing):
                length = right - left + 1
                if length < best_length:
                    best_start, best_length = (left, length)
                old = s[left]
                if old in missing:
                    if missing[old] == 0:
                        satisfied -= 1
                    missing[old] += 1
                left += 1
        return '' if best_length > len(s) else s[best_start:best_start + best_length]
```

**复杂度：** 时间 \(O(m+n)\)，辅助空间 \(O(|\Sigma|)\)；\(m,n\) 为两字符串长度，输出另计。

#### 补充：直接比较窗口是否覆盖所需计数

右端不断加入字符。只要窗口中每种字符的数量都不少于 `t` 的要求，就尝试更新最短答案，并移出一个左端字符继续缩短。失去覆盖条件后，再扩展右端。

```python
from collections import Counter

class Solution:
    def minWindow(self, s, t):
        required = Counter(t)
        window = Counter()
        begin = 0
        best_begin, best_end = -1, len(s)
        for end, char in enumerate(s):
            window[char] += 1
            while window >= required:
                if end - begin < best_end - best_begin:
                    best_begin, best_end = begin, end
                window[s[begin]] -= 1
                begin += 1
        return '' if best_begin == -1 else s[best_begin:best_end + 1]
```

**复杂度：** 时间 \(O(|s|\Sigma + |t|)\)，空间 \(O(\Sigma)\)；Σ 为字符集大小。

**注意：** 每次覆盖检查都比较字符计数；主解法用已满足的字符种数省去逐项比较。


## 普通数组

### 最大子数组和（LeetCode 53）

中等 · [力扣原题](https://leetcode.cn/problems/maximum-subarray/) · [灵茶山艾府题解](https://leetcode.cn/problems/maximum-subarray/solutions/2533977/qian-zhui-he-zuo-fa-ben-zhi-shi-mai-mai-abu71/)

#### 题面

给定整数数组 `nums`，从中选择一段非空、连续的元素，使这一段的总和最大。返回这个最大总和。

不能跳过中间元素，也不能选择空数组。如果所有数都是负数，仍须选出至少一个元素。

**数据范围与约定**

- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

**进阶要求**

- 如果你已经实现复杂度为 \(O(n)\) 的解法，尝试使用更为精妙的 分治法 求解。

**示例**

`[-3,4,-1,2,-5]` 返回 `5`，对应子数组 `[4,-1,2]`。

#### 解法：当前前缀和减去最小历史前缀和

一段子数组的和，等于右端累计和减去起点前的累计和。因此扫描到每个右端时，用当前累计和减去此前最小累计和，就得到以它结尾的最大和。先更新答案，再记录新的最小前缀，保证选择的子数组非空。

```python
class Solution:

    def maxSubArray(self, nums):
        prefix = smallest = 0
        best = float('-inf')
        for value in nums:
            prefix += value
            best = max(best, prefix - smallest)
            smallest = min(smallest, prefix)
        return best
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

#### 补充：动态规划数组

`ending[i]` 表示以下标 i 结尾的最大子数组和。前一段和为正就接上，否则从当前数重新开始。最后在所有结尾中取最大值；答案不能包含空子数组。

```python
class Solution:
    def maxSubArray(self, nums):
        ending = [nums[0]]
        for value in nums[1:]:
            ending.append(value + max(0, ending[-1]))
        return max(ending)
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)。

#### 补充：动态规划只保留上一项

当前结尾的最优和只依赖上一个结尾，因此用 `ending` 代替整个数组；`best` 保存扫描过的所有结尾的最大值。负的上一段只会拖低总和，应舍弃。

```python
class Solution:
    def maxSubArray(self, nums):
        ending = 0
        best = nums[0]
        for value in nums:
            ending = value + max(ending, 0)
            best = max(best, ending)
        return best
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 与前缀和法同为线性时间、常数额外空间。

### 合并区间（LeetCode 56）

中等 · [力扣原题](https://leetcode.cn/problems/merge-intervals/) · [灵茶山艾府题解](https://leetcode.cn/problems/merge-intervals/solutions/2798138/jian-dan-zuo-fa-yi-ji-wei-shi-yao-yao-zh-f2b3/)

#### 题面

给定区间数组 `intervals`，每项 `[start,end]` 表示一个包含左右端点的区间。把有重叠的区间合并，返回合并后互不重叠的区间。

合并前后覆盖的数值范围必须相同。共用端点也算重叠，例如 `[1,3]` 和 `[3,5]` 应合成 `[1,5]`；输入区间不一定有序。

**数据范围与约定**

- `1 <= intervals.length <= 10^4`
- `intervals[i].length == 2`
- `0 <= start_i <= end_i <= 10^4`

**示例**

`[[5,7],[1,3],[3,6]]` 返回 `[[1,7]]`，三个区间相互衔接，合起来连续覆盖 `1` 到 `7`。

#### 解法：按左端点排序后合并

排序后，新区间只需与结果中的最后一段比较。若新起点不超过上一段终点，就把终点扩大到两者较大值；否则新增一段。端点相等也算重叠。

```python
class Solution:

    def merge(self, intervals):
        intervals.sort(key=lambda interval: interval[0])
        answer = []
        for interval in intervals:
            if answer and interval[0] <= answer[-1][1]:
                answer[-1][1] = max(answer[-1][1], interval[1])
            else:
                answer.append(interval)
        return answer
```

**复杂度：** 时间 \(O(n\log n)\)，辅助空间 \(O(n)\)，来自 Python 排序；不计结果。

**注意：** 会重排输入列表，并可能修改其中区间的右端点。

#### 补充：排序后在一组合并结束时输出

按左端点排序，用 `left`、`right` 记录正在合并的一组。读入区间后扩大这组的边界；若下一段起点超过 `right`，当前组已经完整，可以输出。

```python
from math import inf

class Solution:
    def merge(self, intervals):
        intervals.sort(key=lambda pair: pair[0])
        answer = []
        left, right = inf, -inf
        for pos, (start, end) in enumerate(intervals):
            left = min(left, start)
            right = max(right, end)
            if pos + 1 == len(intervals) or intervals[pos + 1][0] > right:
                answer.append([left, right])
                left = inf
        return answer
```

**复杂度：** 时间 \(O(n \log n)\)，除答案外额外空间 \(O(n)\)，来自 Python 排序。

**注意：** 修改输入外层数组的顺序；输出区间为新列表，不复用输入中的区间对象。

#### 补充：坐标翻倍的差分数组

先把端点乘二，再在起点加一、终点后一格减一，扫描累加得到覆盖数量。数量由零变正时开始一段，由正变零时结束。乘二保留了整数端点之间的空隙，使 `[1,2]` 与 `[3,4]` 分开，而 `[1,2]` 与 `[2,3]` 合并。

```python
class Solution:
    def merge(self, intervals):
        largest = max(end for _, end in intervals)
        delta = [0] * (2 * largest + 2)
        for begin, end in intervals:
            delta[2 * begin] += 1
            delta[2 * end + 1] -= 1
        answer = []
        cover = 0
        segment = -1
        for coordinate, change in enumerate(delta):
            cover += change
            if cover > 0 and segment == -1:
                segment = coordinate
            elif cover == 0 and segment != -1:
                answer.append([segment // 2, coordinate // 2])
                segment = -1
        return answer
```

**复杂度：** 时间 \(O(n+U)\)，额外空间 \(O(U)\)，U 为最大右端点。

**注意：** 依赖本题非负且有限的坐标范围；坐标很大时不如排序法。

#### 补充：只扫描出现过的端点

用字典记录每个起点的 +1、终点的 −1，同一坐标先合并变化量。按坐标递增扫描，维护当前覆盖数量：更新前为零就记下新起点，更新后为零就输出区间。共用端点会自然接在一起，单点区间也能保留。

```python
from collections import defaultdict

class Solution:
    def merge(self, intervals):
        changes = defaultdict(int)
        for begin, end in intervals:
            changes[begin] += 1
            changes[end] -= 1
        answer = []
        active = 0
        for position in sorted(changes):
            if active == 0:
                begin = position
            active += changes[position]
            if active == 0:
                answer.append([begin, position])
        return answer
```

**复杂度：** 时间 \(O(n \log n)\)，额外空间 \(O(n)\)。

**注意：** 不遍历没有出现的坐标，不修改输入区间。

### 轮转数组（LeetCode 189）

中等 · [力扣原题](https://leetcode.cn/problems/rotate-array/) · [灵茶山艾府题解](https://leetcode.cn/problems/rotate-array/solutions/2784427/tu-jie-yuan-di-zuo-fa-yi-tu-miao-dong-py-ryfv/)

#### 题面

给定整数数组 `nums` 和非负整数 `k`，把整个数组向右移动 `k` 个位置。右端移出去的元素按顺序回到数组左端，得到轮转后的数组。

需要修改原数组，不要求返回新数组。`k` 可以大于数组长度；移动整整一圈后，数组顺序与原来相同。

**数据范围与约定**

- `1 <= nums.length <= 10^5`
- `-2^31 <= nums[i] <= 2^31 - 1`
- `0 <= k <= 10^5`

**进阶要求**

- 尽可能想出更多的解决方案，至少有 三种 不同的方法可以解决这个问题。
- 你可以使用空间复杂度为 \(O(1)\) 的 原地 算法解决这个问题吗？

**示例**

`[1,2,3,4,5]` 向右移 `2` 位，变为 `[4,5,1,2,3]`；最后两个元素移到了最前面。

#### 解法：三次原地反转

先令 `k` 对数组长度取余。把数组分成前段和最后 `k` 个元素两段：整体反转后，后段到了前面，但两段内部都倒序了；再分别反转这两段，就恢复各自顺序，完成右移。

```python
class Solution:

    def rotate(self, nums, k):
        n = len(nums)
        k %= n

        def reverse(left, right):
            while left < right:
                nums[left], nums[right] = (nums[right], nums[left])
                left += 1
                right -= 1
        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度，反转采用原地交换。

### 除了自身以外数组的乘积（LeetCode 238）

中等 · [力扣原题](https://leetcode.cn/problems/product-of-array-except-self/) · [灵茶山艾府题解](https://leetcode.cn/problems/product-of-array-except-self/solutions/2783788/qian-hou-zhui-fen-jie-fu-ti-dan-pythonja-86r1/)

#### 题面

给定整数数组 `nums`，返回一个同长度数组 `answer`。其中 `answer[i]` 等于 `nums` 中除第 `i` 个位置以外所有元素的乘积。

不能使用除法，要求 \(O(n)\) 时间。数组可能包含零和负数。

**数据范围与约定**

- `2 <= nums.length <= 10^5`
- `-30 <= nums[i] <= 30`
- `输入 保证 数组 answer[i] 在 32 位 整数范围内`

**进阶要求**

- 你可以在 \(O(1)\) 的额外空间复杂度内完成这个题目吗？（ 出于对空间复杂度分析的目的，输出数组 不被视为 额外空间。）

**示例**

`[2,3,4]` 返回 `[12,8,6]`，例如下标 `1` 的答案为 `2×4=8`。

#### 解法：答案存右侧乘积，变量存左侧乘积

每个答案等于该位置左侧所有数的乘积，再乘右侧所有数的乘积。先从右向左，把右侧乘积写入答案数组；再从左向右，用一个变量累计左侧乘积，乘到对应答案上。两端没有元素的一侧，乘积按 `1` 处理。

```python
class Solution:

    def productExceptSelf(self, nums):
        answer = [1] * len(nums)
        suffix = 1
        for i in range(len(nums) - 1, -1, -1):
            answer[i] = suffix
            suffix *= nums[i]
        prefix = 1
        for i, value in enumerate(nums):
            answer[i] *= prefix
            prefix *= value
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)，不计返回数组；\(n\) 为数组长度。

#### 补充：分别保存前缀积与后缀积

`left[i]` 只乘 i 左边的数，`right[i]` 只乘 i 右边的数，二者相乘恰好排除了 `nums[i]`。两端的空乘积设为 1，因此不需要处理除零。

```python
class Solution:
    def productExceptSelf(self, nums):
        size = len(nums)
        left = [1] * size
        right = [1] * size
        for pos in range(1, size):
            left[pos] = left[pos - 1] * nums[pos - 1]
        for pos in range(size - 2, -1, -1):
            right[pos] = right[pos + 1] * nums[pos + 1]
        return [left[pos] * right[pos] for pos in range(size)]
```

**复杂度：** 时间 \(O(n)\)，除答案外额外空间 \(O(n)\)。

**注意：** 满足不用除法和线性时间；进阶的常数额外空间需要使用主解法。

### 缺失的第一个正数（LeetCode 41）

困难 · [力扣原题](https://leetcode.cn/problems/first-missing-positive/) · [灵茶山艾府题解](https://leetcode.cn/problems/first-missing-positive/solutions/3655377/huan-zuo-wei-tong-guo-li-zi-li-jie-suan-qa94e/)

#### 题面

给定未排序的整数数组 `nums`，找出没有出现在数组中的最小正整数，并返回它。正整数从 1 开始。

例如数组中有 1、3、4，却没有 2，答案就是 2；零和负数不能填补正整数位置。必须在 \(O(n)\) 时间内完成，并只用 \(O(1)\) 额外空间；可以修改输入数组。

**数据范围与约定**

- `1 <= nums.length <= 10^5`
- `-2^31 <= nums[i] <= 2^31 - 1`

**示例**

`[3,-2,1,1]` 返回 `2`：数组有 `1` 和 `3`，缺少的最小正整数是 `2`。

#### 解法：把正整数放到对应下标

长度为 `n` 时，答案一定在 `1` 到 `n+1` 之间。遇到范围内的数 `x`，就把它交换到下标 `x-1`；当前位置换入的数继续处理。如果目标位置已经是 `x`，便停止，避免重复值反复交换。最后从头找第一个值不等于下标加一的位置。

```python
class Solution:

    def firstMissingPositive(self, nums):
        n = len(nums)
        for i in range(n):
            while 1 <= nums[i] <= n:
                target = nums[i] - 1
                if nums[target] == nums[i]:
                    break
                nums[i], nums[target] = (nums[target], nums[i])
        for i, value in enumerate(nums):
            if value != i + 1:
                return i + 1
        return n + 1
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。每次有效交换都会固定一个位置。

**注意：** 会修改输入数组。


## 矩阵

### 矩阵置零（LeetCode 73）

中等 · [力扣原题](https://leetcode.cn/problems/set-matrix-zeroes/) · [灵茶山艾府题解](https://leetcode.cn/problems/set-matrix-zeroes/solutions/3799648/yi-bu-bu-you-hua-cong-omn-dao-o1-kong-ji-fdgt/)

#### 题面

给定整数矩阵 `matrix`。如果某个位置原本的值是零，就把它所在的整行和整列都改成零。直接在原矩阵上完成修改。

哪些行列要清零，应根据修改前的矩阵判断。修改过程中产生的新零，不会再触发新的清零操作。函数不需要返回新矩阵。

**数据范围与约定**

- `m == matrix.length`
- `n == matrix[0].length`
- `1 <= m, n <= 200`
- `-2^31 <= matrix[i][j] <= 2^31 - 1`

**进阶要求**

- 一个直观的解决方案是使用 \(O( m n )\) 的额外空间，但这并不是一个好的解决方案。
- 一个简单的改进方案是使用 \(O( m + n )\) 的额外空间，但这仍然不是最好的解决方案。
- 你能想出一个仅使用常量空间的解决方案吗？

**示例**

`[[1,0,3],[4,5,6]]` 改为 `[[0,0,0],[4,0,6]]`，原来的零使首行和第二列清零。

#### 解法：借用第一行、第一列记录清零标记

先分别记住首行、首列是否原本含零。扫描内部格子，遇到零就把对应的首行、首列位置置零，作为标记。标记全部完成后再清零内部格子，最后按原先记录处理首行、首列，避免新写入的零干扰判断。

```python
class Solution:

    def setZeroes(self, matrix):
        m, n = (len(matrix), len(matrix[0]))
        first_row = any((value == 0 for value in matrix[0]))
        first_col = any((matrix[i][0] == 0 for i in range(m)))
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        if first_row:
            for j in range(n):
                matrix[0][j] = 0
        if first_col:
            for i in range(m):
                matrix[i][0] = 0
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(1)\)；\(m,n\) 为矩阵行列数。

#### 补充：用两个数组标记含零的行和列

先读取原矩阵，分别记录哪些行、哪些列包含零；全部记录完成后再修改矩阵。这样新写入的零不会被误认为原有的零。

```python
class Solution:
    def setZeroes(self, matrix):
        rows = [0 in row for row in matrix]
        columns = [0 in column for column in zip(*matrix)]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if rows[i] or columns[j]:
                    matrix[i][j] = 0
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(m+n)\)。

**注意：** 比复用第一行、第一列的方法更直观，但未达到常数额外空间的进阶要求。

**写法补充：** 常数空间版本还可调整首行、首列标志的保存和处理顺序，均使用矩阵边缘作标记。

### 螺旋矩阵（LeetCode 54）

中等 · [力扣原题](https://leetcode.cn/problems/spiral-matrix/) · [灵茶山艾府题解](https://leetcode.cn/problems/spiral-matrix/solutions/2966229/liang-chong-fang-fa-jian-ji-gao-xiao-pyt-4wzk/)

#### 题面

给定矩阵 `matrix`，从左上角出发，按顺时针螺旋顺序读出所有元素，返回一个列表。先从左到右读最上面一行，再沿右边向下、下边向左、左边向上，随后继续向内读取。

每个元素必须恰好读到一次。矩阵不一定是方阵，也可能只有一行或一列。

**数据范围与约定**

- `m == matrix.length`
- `n == matrix[i].length`
- `1 <= m, n <= 10`
- `-100 <= matrix[i][j] <= 100`

**示例**

`[[1,2,3],[4,5,6]]` 返回 `[1,2,3,6,5,4]`：先读上边，再读右边，最后向左读完下边。

#### 解法：按每段长度依次向右、下、左、上走

对 `m` 行、`n` 列矩阵，各段依次走 `n、m-1、n-1、m-2` 格，之后继续缩短。每走完一段就转向，并扣掉已走过的一条边。代码中的两个长度变量会交换角色，表示接下来横向、纵向还需走多少格，不再是固定的原矩阵尺寸。

```python
class Solution:

    def spiralOrder(self, matrix):
        rows, columns = (len(matrix), len(matrix[0]))
        i, j = (0, -1)
        di, dj = (0, 1)
        answer = []
        while columns:
            for _ in range(columns):
                i, j = (i + di, j + dj)
                answer.append(matrix[i][j])
            di, dj = (dj, -di)
            rows, columns = (columns, rows - 1)
        return answer
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(1)\)，输出另计；\(m,n\) 为矩阵行列数。

#### 补充：走过的位置直接标记

从左上角向右出发，方向按右、下、左、上循环。读出一个格子后把它改为 `None`；若下一步越界或遇到 `None`，就右转。总共读取格子数那么多次便结束。

```python
class Solution:
    def spiralOrder(self, matrix):
        moves = ((0, 1), (1, 0), (0, -1), (-1, 0))
        rows, columns = len(matrix), len(matrix[0])
        row = column = direction = 0
        answer = []
        for _ in range(rows * columns):
            answer.append(matrix[row][column])
            matrix[row][column] = None
            dr, dc = moves[direction]
            nr, nc = row + dr, column + dc
            if not (0 <= nr < rows and 0 <= nc < columns) or matrix[nr][nc] is None:
                direction = (direction + 1) % 4
            dr, dc = moves[direction]
            row += dr
            column += dc
        return answer
```

**复杂度：** 时间 \(O(mn)\)，除答案外额外空间 \(O(1)\)。

**注意：** 会把输入矩阵全部改成 `None`；按剩余边长遍历的主解法保留原矩阵。

### 旋转图像（LeetCode 48）

中等 · [力扣原题](https://leetcode.cn/problems/rotate-image/) · [灵茶山艾府题解](https://leetcode.cn/problems/rotate-image/solutions/3655166/shu-xue-ben-zhi-liang-ci-fan-zhuan-deng-aon4a/)

#### 题面

给定一个 `n` 行、`n` 列的矩阵 `matrix`，把它所表示的图像顺时针旋转 90 度。

必须直接修改原矩阵，不能创建另一个同样大小的矩阵来保存旋转结果。函数不需要返回新矩阵。

**数据范围与约定**

- `n == matrix.length == matrix[i].length`
- `1 <= n <= 20`
- `-1000 <= matrix[i][j] <= 1000`

**示例**

`[[1,2],[3,4]]` 顺时针旋转后为 `[[3,1],[4,2]]`，原来的第一列成为第一行。

#### 解法：转置后逐行左右反转

先交换主对角线两侧的元素，也就是把行、列对调；再把每行左右反转。这两步合起来正好是顺时针旋转 90 度。转置时只遍历对角线一侧，避免同一对元素交换两次。

```python
class Solution:

    def rotate(self, matrix):
        n = len(matrix)
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = (matrix[j][i], matrix[i][j])
        for row in matrix:
            left, right = (0, n - 1)
            while left < right:
                row[left], row[right] = (row[right], row[left])
                left += 1
                right -= 1
```

**复杂度：** 时间 \(O(n^2)\)，额外空间 \(O(1)\)；\(n\) 为方阵边长。

**写法补充：** 另一写法按行完成转置交换后立即左右反转该行，两步变换相同。

### 搜索二维矩阵 II（LeetCode 240）

中等 · [力扣原题](https://leetcode.cn/problems/search-a-2d-matrix-ii/) · [灵茶山艾府题解](https://leetcode.cn/problems/search-a-2d-matrix-ii/solutions/2783938/tu-jie-pai-chu-fa-yi-tu-miao-dong-python-kytg/)

#### 题面

给定矩阵 `matrix` 和整数 `target`。矩阵每行从左到右、每列从上到下都按从小到大排列，判断矩阵中是否存在 `target`，返回布尔值。

这些条件只保证各行、各列分别有序，不保证把所有行接起来后仍有序。矩阵可能是长方形。

**数据范围与约定**

- `m == matrix.length`
- `n == matrix[i].length`
- `1 <= n, m <= 300`
- `-10^9 <= matrix[i][j] <= 10^9`
- 每行的所有元素从左到右升序排列
- 每列的所有元素从上到下升序排列
- `-10^9 <= target <= 10^9`

**示例**

在 `[[1,4,7],[2,5,8],[3,6,9]]` 中查找 `6`，返回 `True`。

#### 解法：从右上角排除整行或整列

从右上角开始比较。当前值大于目标时，它下面的值也都太大，向左移一列；当前值小于目标时，它左边的值也都太小，向下移一行。每次排除一整行或一整列，找到目标便返回成功，走出矩阵则失败。

```python
class Solution:

    def searchMatrix(self, matrix, target):
        row, col = (0, len(matrix[0]) - 1)
        while row < len(matrix) and col >= 0:
            value = matrix[row][col]
            if value == target:
                return True
            if value > target:
                col -= 1
            else:
                row += 1
        return False
```

**复杂度：** 时间 \(O(m+n)\)，额外空间 \(O(1)\)；\(m,n\) 为矩阵行列数。


## 链表

### 相交链表（LeetCode 160）

简单 · [力扣原题](https://leetcode.cn/problems/intersection-of-two-linked-lists/) · [灵茶山艾府题解](https://leetcode.cn/problems/intersection-of-two-linked-lists/solutions/2958778/tu-jie-yi-zhang-tu-miao-dong-xiang-jiao-m6tg1/)

#### 题面

给定两条单链表的头节点 `headA` 和 `headB`，找出两条链表开始共享的第一个节点，返回该节点；如果没有共享节点，返回 `None`。

“相交”要求指向同一个节点对象，仅节点值相同不算。两条链表都没有环，处理后应保持原有连接。样例里的 `skipA`、`skipB` 表示各头到交点的距离，`intersectVal` 表示交点值，它们不是函数参数。

**数据范围与约定**

- listA 中节点数目为 m
- listB 中节点数目为 n
- `1 <= m, n <= 3 * 10^4`
- `1 <= Node.val <= 10^5`
- `0 <= skipA <= m`
- `0 <= skipB <= n`
- 如果 listA 和 listB 没有交点， intersectVal 为 0
- `如果 listA 和 listB 有交点， intersectVal == listA[skipA] == listB[skipB]`

**进阶要求**

- 你能否设计一个时间复杂度 \(O(m + n)\) 、仅用 \(O(1)\) 内存的解决方案？

**示例**

A 为 `1→2→8→9`，B 为 `3→8→9`，其中 `8、9` 是共享节点，则返回节点 `8`。

#### 解法：两指针各走完两条链表

两个指针分别从两条链表头出发，走到空后改从另一条链表头继续。交换路线抵消了两条链表的长度差：若相交，它们会在同一个公共节点相遇；若不相交，最终同时为空。

```python
class Solution:

    def getIntersectionNode(self, headA, headB):
        a, b = (headA, headB)
        while a is not b:
            a = headB if a is None else a.next
            b = headA if b is None else b.next
        return a
```

**复杂度：** 时间 \(O(m+n)\)，额外空间 \(O(1)\)；\(m,n\) 为两条链表的长度。

**注意：** 比较节点对象是否相同，不能只比较节点值。

### 反转链表（LeetCode 206）

简单 · [力扣原题](https://leetcode.cn/problems/reverse-linked-list/) · [灵茶山艾府题解](https://leetcode.cn/problems/reverse-linked-list/solutions/1992225/you-xie-cuo-liao-yi-ge-shi-pin-jiang-tou-o5zy/)

#### 题面

给定单链表的头节点 `head`，把整条链表的连接方向反转，并返回反转后的头节点。

例如 `2→5→7` 反转后是 `7→5→2`。输入可以是空链表，此时返回 `None`。

**数据范围与约定**

- `链表中节点的数目范围是 [0, 5000]`
- `-5000 <= Node.val <= 5000`

**进阶要求**

- 链表可以选用迭代或递归方式完成反转。你能否用两种方法解决这道题？

**示例**

`2→5→7` 反转为 `7→5→2`。

#### 解法：逐个反转指针

维护已反转部分的头和当前待处理节点。每轮先保存当前节点的后继，再让当前节点指向已反转部分，最后推进两个指针。原链表走完后，已反转部分的头就是新头节点。

```python
class Solution:

    def reverseList(self, head):
        result = None
        while head:
            following = head.next
            head.next = result
            result = head
            head = following
        return result
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为节点数。

#### 补充：递归到末尾，再反向接回

递归先处理 `head` 后面的链表。返回时，原来的下一个节点已经成为那段反转链表的尾部，让它指向 `head`，再断开 `head` 原来的 `next`，避免形成环。每层都返回同一个新头节点。

```python
class Solution:
    def reverseList(self, head):
        if head is None or head.next is None:
            return head
        new_head = self.reverseList(head.next)
        head.next.next = head
        head.next = None
        return new_head
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(n)\)。

**注意：** 递归简洁，但迭代法只需常数额外空间。

### 回文链表（LeetCode 234）

简单 · [力扣原题](https://leetcode.cn/problems/palindrome-linked-list/) · [灵茶山艾府题解](https://leetcode.cn/problems/palindrome-linked-list/solutions/2952645/o1-kong-jian-zuo-fa-xun-zhao-zhong-jian-rv0f3/)

#### 题面

给定单链表的头节点 `head`，判断从头到尾读出的节点值是否正着读、反着读都一样。一样返回 `True`，否则返回 `False`。

例如 `1→2→2→1` 是回文，`1→2` 不是。

**数据范围与约定**

- `链表中节点数目在范围 [1, 10^5] 内`
- `0 <= Node.val <= 9`

**进阶要求**

- 你能否用 \(O(n)\) 时间复杂度和 \(O(1)\) 空间复杂度解决此题？

**示例**

`1→4→4→1` 返回 `True`；`1→4→2→1` 返回 `False`，因为从两端数的第二个值不同。

#### 解法：反转后半段，比较后恢复

用快慢指针找到中间位置，反转从这里开始的链表，再从原头部和反转后的头部同步比较。后半段比完即可；奇数长度时，中点会与自身比较，不影响结果。最后再次反转后半段，恢复原链表。

```python
class Solution:

    def isPalindrome(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        def reverse(node):
            result = None
            while node:
                following = node.next
                node.next = result
                result = node
                node = following
            return result
        second = reverse(slow)
        a, b = (head, second)
        equal = True
        while b:
            if a.val != b.val:
                equal = False
                break
            a, b = (a.next, b.next)
        reverse(second)
        return equal
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为节点数。

#### 补充：递归回退时从两端比较

递归先走到尾节点，再沿调用栈向前返回，相当于从右向左访问链表。同时让 `left` 从头向后走。每次比较两端对应的节点，任何一对不同都立即返回 `False`。

```python
class Solution:
    def isPalindrome(self, head):
        left = head
        def compare(right):
            nonlocal left
            if right.next is not None and not compare(right.next):
                return False
            if left.val != right.val:
                return False
            left = left.next
            return True
        return compare(head)
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(n)\)。

**注意：** 保留原链表，但递归栈不满足常数空间的进阶目标。

#### 补充：反转后半段后比较，不恢复链表

快慢指针找到中间位置，把从中间开始的链表反转。随后分别从原头部和反转后的头部向前比较；较短的后半段比完即可，奇数长度时中间节点会与自身比较。

```python
class Solution:
    def isPalindrome(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        previous = None
        while slow:
            following = slow.next
            slow.next = previous
            previous, slow = slow, following
        first, second = head, previous
        while second:
            if first.val != second.val:
                return False
            first, second = first.next, second.next
        return True
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 返回后保留反转造成的指针变化。需要保留原链表时使用主解法中的恢复步骤。

### 环形链表（LeetCode 141）

简单 · [力扣原题](https://leetcode.cn/problems/linked-list-cycle/) · [灵茶山艾府题解](https://leetcode.cn/problems/linked-list-cycle/solutions/1999269/mei-xiang-ming-bai-yi-ge-shi-pin-jiang-t-c4sw/)

#### 题面

给定单链表的头节点 `head`，判断链表中是否有环，返回布尔值。如果沿着 `next` 不断前进，会再次到达已经经过的同一个节点，就说明存在环。

节点值可以重复，因此不能仅凭值相同判断有环。样例中的 `pos` 表示尾节点连接到的下标，`-1` 表示不连接任何前面的节点；`pos` 不会作为函数参数传入。

**数据范围与约定**

- `链表中节点的数目范围是 [0, 10^4]`
- `-10^5 <= Node.val <= 10^5`
- pos 为 -1 或者链表中的一个 有效索引 。

**进阶要求**

- 你能用 \(O(1)\) （即，常量）内存解决此问题吗？

**示例**

`1→2→3` 的尾节点重新指向节点 `2` 时有环，返回 `True`；尾节点指向空时返回 `False`。

#### 解法：快慢指针判断是否相遇

慢指针每轮走一步，快指针走两步。无环时快指针会到达空；有环时，进入环后快指针每轮比慢指针多走一步，最终一定追上。每次移动前先检查快指针及其后继是否存在。

```python
class Solution:

    def hasCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow, fast = (slow.next, fast.next.next)
            if slow is fast:
                return True
        return False
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为不同节点的个数。

### 环形链表 II（LeetCode 142）

中等 · [力扣原题](https://leetcode.cn/problems/linked-list-cycle-ii/) · [灵茶山艾府题解](https://leetcode.cn/problems/linked-list-cycle-ii/solutions/1999271/mei-xiang-ming-bai-yi-ge-shi-pin-jiang-t-nvsq/)

#### 题面

给定单链表的头节点 `head`，如果链表有环，返回从头开始沿 `next` 行走时首次进入环的那个节点；如果没有环，返回 `None`。

不允许修改链表连接。样例中的 `pos` 表示尾节点所连接的下标，`-1` 表示无环；函数只接收 `head`，不会得到 `pos`。

**数据范围与约定**

- `链表中节点的数目范围在范围 [0, 10^4] 内`
- `-10^5 <= Node.val <= 10^5`
- pos 的值为 -1 或者链表中的一个有效索引

**进阶要求**

- 你是否可以使用 \(O(1)\) 空间解决此题？

**示例**

`1→2→3→4` 的尾节点连回节点 `2`，应返回节点 `2`，而不是第一次相遇的节点。

#### 解法：先找相遇点，再找环入口

先用快慢指针判断有环并找到相遇点。然后让一个指针回到头节点，另一个留在相遇点；两者每次都走一步，再次相遇处就是入口。

原因是：第一次相遇时，快指针比慢指针多走的距离等于慢指针已走的距离，而这个差必是整圈数。因此，从头到入口的路程，恰好能让相遇点上的指针也绕回入口。

```python
class Solution:

    def detectCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow, fast = (slow.next, fast.next.next)
            if slow is fast:
                entrance = head
                while entrance is not slow:
                    entrance, slow = (entrance.next, slow.next)
                return entrance
        return None
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为不同节点的个数。

### 合并两个有序链表（LeetCode 21）

简单 · [力扣原题](https://leetcode.cn/problems/merge-two-sorted-lists/) · [灵茶山艾府题解](https://leetcode.cn/problems/merge-two-sorted-lists/solutions/2373691/liang-chong-fang-fa-die-dai-di-gui-pytho-wf75/)

#### 题面

给定两条已按节点值从小到大排列的链表 `list1`、`list2`，把它们的节点合并成一条同样有序的链表，返回合并后链表的头节点。

每条输入链表都可能为空，值相同的节点都要保留。合并是把给定链表的节点重新连接起来。

**数据范围与约定**

- `两个链表的节点数目范围是 [0, 50]`
- `-100 <= Node.val <= 100`
- l1 和 l2 均按 非递减顺序 排列

**示例**

`1→4` 与 `2→3` 合并为 `1→2→3→4`。

#### 解法：每次接入较小的头节点

两条链表都已排序，所以当前两个头节点中较小的那个，就是所有剩余节点中的最小值。把它接到结果尾部，推进对应链表。某一条用完后，直接接上另一条剩余部分。辅助头节点用于统一处理结果的开头。

```python
class Solution:

    def mergeTwoLists(self, list1, list2):
        dummy = ListNode()
        tail = dummy
        while list1 and list2:
            if list1.val < list2.val:
                tail.next, list1 = (list1, list1.next)
            else:
                tail.next, list2 = (list2, list2.next)
            tail = tail.next
        tail.next = list1 or list2
        return dummy.next
```

**复杂度：** 时间 \(O(m+n)\)，额外空间 \(O(1)\)；\(m,n\) 为链表长度，复用输入节点。

**注意：** 重新连接输入节点，不另建一整条链表。

#### 补充：递归选择当前较小节点

两条链表中较小的头节点一定是合并结果的头。复用该节点，把剩余部分的合并结果接到它后面。一条链表为空时，另一条可以直接接入。

```python
class Solution:
    def mergeTwoLists(self, list1, list2):
        if list1 is None:
            return list2
        if list2 is None:
            return list1
        if list1.val < list2.val:
            list1.next = self.mergeTwoLists(list1.next, list2)
            return list1
        list2.next = self.mergeTwoLists(list1, list2.next)
        return list2
```

**复杂度：** 时间 \(O(m+n)\)，递归栈 \(O(m+n)\)。

**注意：** 复用输入节点；相等时与原文一样先选第二条链表。

### 两数相加（LeetCode 2）

中等 · [力扣原题](https://leetcode.cn/problems/add-two-numbers/) · [灵茶山艾府题解](https://leetcode.cn/problems/add-two-numbers/solutions/2327008/dong-hua-jian-ji-xie-fa-cong-di-gui-dao-oe0di/)

#### 题面

给定两条非空链表 `l1`、`l2`，分别表示两个非负整数。每个节点存一位十进制数字，个位在链表头部，后面依次是十位、百位。求两数之和，并用同样的方式返回结果链表。

例如 `7→8` 表示 87。每个节点值都在 0 到 9 之间；除数字 0 本身外，输入整数没有多余的前导零。两条链表长度可以不同。

**数据范围与约定**

- `每个链表中的节点数在范围 [1, 100] 内`
- `0 <= Node.val <= 9`
- 题目数据保证列表表示的数字不含前导零

**示例**

`7→8` 与 `6→1` 分别表示 `87` 和 `16`，相加为 `103`，返回 `3→0→1`。

#### 解法：模拟竖式加法

链表从个位开始，正好可以逐位相加。把当前两位和进位相加，除以 `10` 的余数写入新节点，商作为下一位进位。较短链表缺少的位按零处理；两条链表都结束后，也要处理可能剩下的进位。

```python
class Solution:

    def addTwoNumbers(self, l1, l2):
        dummy = ListNode()
        tail = dummy
        carry = 0
        while l1 or l2 or carry:
            total = carry
            if l1:
                total += l1.val
                l1 = l1.next
            if l2:
                total += l2.val
                l2 = l2.next
            carry, digit = divmod(total, 10)
            tail.next = ListNode(digit)
            tail = tail.next
        return dummy.next
```

**复杂度：** 时间 \(O(\max(m,n))\)，额外空间 \(O(1)\)，输出链表另计；\(m,n\) 为两链表长度。

#### 补充：递归相加，每一位创建新节点

每层把两个当前位置的数位与进位相加；余数是本位，商是下一层的进位。两个链表都结束且没有进位时，结果也结束。

```python
class Solution:
    def addTwoNumbers(self, l1, l2, carry=0):
        if l1 is None and l2 is None and carry == 0:
            return None
        total = carry
        if l1:
            total += l1.val
            l1 = l1.next
        if l2:
            total += l2.val
            l2 = l2.next
        next_carry, digit = divmod(total, 10)
        suffix = self.addTwoNumbers(l1, l2, next_carry)
        return ListNode(digit, suffix)
```

**复杂度：** 时间 \(O(\max(m,n))\)；除新结果外递归栈 \(O(\max(m,n))\)。

**注意：** 不修改输入节点。

#### 补充：递归相加，复用输入节点

始终让 `l1` 指向当前存在的节点，把本位结果写回 `l1`，再递归处理后续数位。若两条链表都结束后仍有进位，只为这个最终进位新建节点。

```python
class Solution:
    def addTwoNumbers(self, l1, l2, carry=0):
        if l1 is None and l2 is None:
            return ListNode(carry) if carry else None
        if l1 is None:
            l1, l2 = l2, l1
        carry, l1.val = divmod(l1.val + (l2.val if l2 else 0) + carry, 10)
        l1.next = self.addTwoNumbers(l1.next, l2.next if l2 else None, carry)
        return l1
```

**复杂度：** 时间 \(O(\max(m,n))\)，递归栈 \(O(\max(m,n))\)，至多额外创建一个结果节点。

**注意：** 修改输入节点的值和连接；虽然几乎不新建节点，递归栈仍占线性空间。

### 删除链表的倒数第 N 个结点（LeetCode 19）

中等 · [力扣原题](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/) · [灵茶山艾府题解](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/solutions/2004057/ru-he-shan-chu-jie-dian-liu-fen-zhong-ga-xpfs/)

#### 题面

给定单链表头节点 `head` 和正整数 `n`，删除从尾部数起的第 `n` 个节点，并返回删除后的头节点。

倒数第一个节点就是尾节点，题目保证 `n` 不超过链表长度。删除的节点也可能是头节点；如果删除后为空，返回 `None`。

**数据范围与约定**

- 链表中结点的数目为 sz
- `1 <= sz <= 30`
- `0 <= Node.val <= 100`
- `1 <= n <= sz`

**进阶要求**

- 你能尝试使用一趟扫描实现吗？

**示例**

`2→4→6→8` 删除倒数第 `2` 个节点后，得到 `2→4→8`。

#### 解法：保持固定间距定位待删节点

在头节点前放一个辅助节点，两个指针都从这里出发。前指针先走 `n+1` 步，再与后指针同步前进。前指针到空时，后指针正好停在待删节点之前，跳过其后继即可。这样删除头节点也无需特判。

```python
class Solution:

    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)
        ahead = behind = dummy
        for _ in range(n + 1):
            ahead = ahead.next
        while ahead:
            ahead, behind = (ahead.next, behind.next)
        behind.next = behind.next.next
        return dummy.next
```

**复杂度：** 时间 \(O(L)\)，额外空间 \(O(1)\)；\(L\) 为链表长度。

### 两两交换链表中的节点（LeetCode 24）

中等 · [力扣原题](https://leetcode.cn/problems/swap-nodes-in-pairs/) · [灵茶山艾府题解](https://leetcode.cn/problems/swap-nodes-in-pairs/solutions/2374872/tu-jie-die-dai-di-gui-yi-zhang-tu-miao-d-51ap/)

#### 题面

给定单链表头节点 `head`，把第一、第二个节点交换，第三、第四个节点交换，以此类推，返回处理后的头节点。

必须交换节点之间的连接，不能只交换节点值。若节点数为奇数，最后一个节点保持不动；空链表也应正常处理。

**数据范围与约定**

- `链表中节点的数目在范围 [0, 100] 内`
- `0 <= Node.val <= 100`

**示例**

`1→2→3→4→5` 变为 `2→1→4→3→5`，最后一个节点保持不动。

#### 解法：每次重连相邻两个节点

把当前一组记为前驱、节点 A、节点 B、后续部分。按“前驱→B→A→后续部分”重新连接，再让 A 成为下一组前驱。头部增加辅助节点，使第一组和后续各组使用同样的逻辑；不足两个节点时结束。

```python
class Solution:

    def swapPairs(self, head):
        dummy = ListNode(0, head)
        before = dummy
        while before.next and before.next.next:
            first = before.next
            second = first.next
            following = second.next
            before.next = second
            second.next = first
            first.next = following
            before = first
        return dummy.next
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为节点数。

#### 补充：递归交换后续节点，再接回当前一对

当前两个节点记为 `first`、`second`。先递归处理 `second` 之后的链表，再让 `first` 指向处理结果、`second` 指向 `first`，返回 `second` 作为这一段的新头。

```python
class Solution:
    def swapPairs(self, head):
        if head is None or head.next is None:
            return head
        first, second = head, head.next
        first.next = self.swapPairs(second.next)
        second.next = first
        return second
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(n)\)。

### K 个一组翻转链表（LeetCode 25）

困难 · [力扣原题](https://leetcode.cn/problems/reverse-nodes-in-k-group/) · [灵茶山艾府题解](https://leetcode.cn/problems/reverse-nodes-in-k-group/solutions/1992228/you-xie-cuo-liao-yi-ge-shi-pin-jiang-tou-plfs/)

#### 题面

给定单链表头节点 `head` 和正整数 `k`，从头开始每 `k` 个节点分成一组，把每个完整组内的节点顺序反转，返回新头节点。

只改变节点连接，不改变节点值。最后一组如果不足 `k` 个节点，必须保持原来的顺序。

**数据范围与约定**

- 链表中的节点数目为 n
- `1 <= k <= n <= 5000`
- `0 <= Node.val <= 1000`

**进阶要求**

- 你可以设计一个只用 \(O(1)\) 额外内存空间的算法解决此问题吗？

**示例**

`1→2→3→4→5`、`k=3`，返回 `3→2→1→4→5`；末尾不足一组，不反转。

#### 解法：先确认够一组，再反转

每轮先向后查看是否还有 `k` 个节点，不足就结束。够一组时，保存下一组起点，反转这一组，再把前一组尾、当前组和剩余链表接好。原组头会变成组尾，下一轮从它后面开始。

```python
class Solution:

    def reverseKGroup(self, head, k):
        dummy = ListNode(0, head)
        before = dummy
        while True:
            last = before
            for _ in range(k):
                last = last.next
                if last is None:
                    return dummy.next
            following = last.next
            first = before.next
            previous, current = (following, first)
            while current is not following:
                nxt = current.next
                current.next = previous
                previous, current = (current, nxt)
            before.next = last
            before = first
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为节点数。

#### 补充：先统计长度，再逐组反转

先算出剩余节点数，只在至少还剩 `k` 个节点时反转。每次保存上一组尾节点，用 `k` 次指针反向完成当前组，然后连接前一组、当前组和尚未处理部分。剩余不足 `k` 个时直接保留。

```python
class Solution:
    def reverseKGroup(self, head, k):
        remaining = 0
        node = head
        while node:
            remaining += 1
            node = node.next
        dummy = ListNode(0, head)
        before = dummy
        while remaining >= k:
            remaining -= k
            old_head = before.next
            node, previous = old_head, None
            for _ in range(k):
                following = node.next
                node.next = previous
                previous, node = node, following
            old_head.next = node
            before.next = previous
            before = old_head
        return dummy.next
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 比主解法多一次完整计数遍历，两者的时间和空间复杂度相同。

### 随机链表的复制（LeetCode 138）

中等 · [力扣原题](https://leetcode.cn/problems/copy-list-with-random-pointer/) · [灵茶山艾府题解](https://leetcode.cn/problems/copy-list-with-random-pointer/solutions/2993775/bu-yong-ha-xi-biao-de-zuo-fa-pythonjavac-nzdo/)

#### 题面

给定一条链表，每个节点除了 `val`、`next`，还有一个 `random` 指针，它可以指向链表中的任意节点，也可以为空。创建这条链表的独立副本，并返回新链表头节点。

新链表的节点值、前后连接及随机指向关系都要与原链表一一对应，但必须使用新节点，任何新指针都不能指向原链表节点。样例中的 `[val,random_index]` 只是节点值和随机目标下标的表示方式，实际输入是头节点 `head`。

**数据范围与约定**

- `0 <= n <= 1000`
- `-10^4 <= Node.val <= 10^4`
- `Node.random` 为 null 或指向链表中的节点。

**示例**

原链为 `5→9`，`5.random` 指向 `9`，`9.random` 指向自己；副本保持相同关系，但所有节点都是新建的。

#### 解法：把副本插在原节点后面

先在每个原节点后插入它的副本，这样原节点的 `next` 就能直接找到对应副本。再设置随机指针：原随机目标的下一个节点，就是副本应指向的目标。最后拆成两条链，返回副本，同时恢复原链表。

```python
class Solution:

    def copyRandomList(self, head):
        current = head
        while current:
            duplicate = Node(current.val)
            duplicate.next = current.next
            current.next = duplicate
            current = duplicate.next
        current = head
        while current:
            current.next.random = current.random.next if current.random else None
            current = current.next.next
        new_head = head.next if head else None
        current = head
        while current:
            duplicate = current.next
            following = duplicate.next
            current.next = following
            duplicate.next = following.next if following else None
            current = following
        return new_head
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)，输出节点另计；\(n\) 为节点数。

#### 补充：交错复制节点，拆出副本但不恢复原链表

先在每个原节点后插入副本，再设置副本的 `random`：原 `random` 目标的 `next` 就是对应副本。最后跳过原节点，把副本串起来。

```python
class Solution:
    def copyRandomList(self, head):
        original = head
        while original:
            original.next = Node(original.val, original.next)
            original = original.next.next
        original = head
        while original:
            if original.random:
                original.next.random = original.random.next
            original = original.next.next
        dummy = Node(0, head)
        tail = dummy
        while tail.next:
            tail.next = tail.next.next
            tail = tail.next
        return dummy.next
```

**复杂度：** 时间 \(O(n)\)，除复制出的结果外额外空间 \(O(1)\)。

**注意：** 不恢复原链表的 `next`；主解法增加恢复步骤，时间和辅助空间仍相同。

### 排序链表（LeetCode 148）

中等 · [力扣原题](https://leetcode.cn/problems/sort-list/) · [灵茶山艾府题解](https://leetcode.cn/problems/sort-list/solutions/2993518/liang-chong-fang-fa-fen-zhi-die-dai-mo-k-caei/)

#### 题面

给定单链表头节点 `head`，把链表按节点值从小到大排序，返回排序后的头节点。

相同值的节点都需要保留，空链表返回 `None`。

**数据范围与约定**

- `链表中节点的数目在范围 [0, 5 * 10^4] 内`
- `-10^5 <= Node.val <= 10^5`

**进阶要求**

- 你可以在 \(O(n \log n)\) 时间复杂度和常数级空间复杂度下，对链表进行排序吗？

**示例**

`4→1→3→2` 排序后为 `1→2→3→4`。

#### 解法：从短段到长段逐轮归并

单个节点天然有序。先把相邻的长度一段合并成长度二段，再合并成长度四段，依次翻倍。每轮切出相邻两段，按值合并并接回结果；最后不足一段的部分照常处理。段长覆盖整条链表时，排序完成。

```python
class Solution:

    def sortList(self, head):
        length = 0
        current = head
        while current:
            length += 1
            current = current.next

        def split(start, size):
            if start is None:
                return None
            for _ in range(size - 1):
                if start.next is None:
                    break
                start = start.next
            rest = start.next
            start.next = None
            return rest
        dummy = ListNode(0, head)
        width = 1
        while width < length:
            before = dummy
            current = dummy.next
            while current:
                left = current
                right = split(left, width)
                current = split(right, width)
                while left and right:
                    if left.val <= right.val:
                        before.next, left = (left, left.next)
                    else:
                        before.next, right = (right, right.next)
                    before = before.next
                before.next = left or right
                while before.next:
                    before = before.next
                before.next = current
            width *= 2
        return dummy.next
```

**复杂度：** 时间 \(O(n\log n)\)，额外空间 \(O(1)\)；\(n\) 为节点数，不使用递归。

**注意：** 只重连输入节点，使用循环而非递归，因此不需要递归栈。

#### 补充：递归归并排序

用快慢指针把链表断成两半，分别递归排好，再按节点值合并。每层合并总共处理全部节点，递归层数为对数级。

```python
class Solution:

    def mergeTwoLists(self, a, b):
        sentinel = ListNode()
        tail = sentinel
        while a and b:
            if a.val < b.val:
                tail.next = a
                a = a.next
            else:
                tail.next = b
                b = b.next
            tail = tail.next
        tail.next = a if a else b
        return sentinel.next

    def sortList(self, head):
        if head is None or head.next is None:
            return head
        slow = fast = head
        previous = None
        while fast and fast.next:
            previous = slow
            slow, fast = slow.next, fast.next.next
        previous.next = None
        left = self.sortList(head)
        right = self.sortList(slow)
        return self.mergeTwoLists(left, right)
```

**复杂度：** 时间 \(O(n \log n)\)，递归栈 \(O(\log n)\)。

**注意：** 复用节点，但递归栈不满足常数额外空间的进阶目标；主解法使用迭代归并。

### 合并 K 个升序链表（LeetCode 23）

困难 · [力扣原题](https://leetcode.cn/problems/merge-k-sorted-lists/) · [灵茶山艾府题解](https://leetcode.cn/problems/merge-k-sorted-lists/solutions/2384305/liang-chong-fang-fa-zui-xiao-dui-fen-zhi-zbzx/)

#### 题面

给定列表 `lists`，其中每一项是一条已按值从小到大排列的链表头节点。把这些链表合并成一条有序链表，返回它的头节点。

不同链表中的相同值都要保留。`lists` 本身可以为空，其中的链表也可以为空；没有任何节点时返回 `None`。

**数据范围与约定**

- `k == lists.length`
- `0 <= k <= 10^4`
- `0 <= lists[i].length <= 500`
- `-10^4 <= lists[i][j] <= 10^4`
- `lists[i] 按 升序 排列`
- `lists[i].length 的总和不超过 10^4`

**示例**

`1→6`、`2→4`、`3` 合并为 `1→2→3→4→6`。

#### 解法：最小堆保存每条链表的当前头

每条链表剩余节点中的最小值就在头部。把各条非空链表的头放入最小堆，每次取出值最小的节点接入结果，再把它的后继放进堆。堆中每条链表至多保留一个候选，始终能取到全部剩余节点中的最小值。

```python
import heapq

class Solution:

    def mergeKLists(self, lists):
        heap = []
        for index, node in enumerate(lists):
            if node:
                heap.append((node.val, index, node))
        heapq.heapify(heap)
        dummy = ListNode()
        tail = dummy
        while heap:
            _, index, node = heapq.heappop(heap)
            following = node.next
            tail.next = node
            tail = node
            if following:
                heapq.heappush(heap, (following.val, index, following))
        tail.next = None
        return dummy.next
```

**复杂度：** 时间 \(O(k+N\log(k+1))\)，辅助空间 \(O(k)\)；\(N\) 为总节点数，\(k\) 为链表数。

**注意：** 复用并重新连接输入节点。

#### 补充：递归分治合并

把 `lists` 分成两半，各自递归合成一条链，再合并这两条有序链。每个节点最多参与对数级轮数的合并。

```python
class Solution:

    def mergeTwoLists(self, a, b):
        sentinel = ListNode()
        tail = sentinel
        while a and b:
            if a.val < b.val:
                tail.next = a
                a = a.next
            else:
                tail.next = b
                b = b.next
            tail = tail.next
        tail.next = a if a else b
        return sentinel.next

    def mergeKLists(self, lists):
        count = len(lists)
        if count == 0:
            return None
        if count == 1:
            return lists[0]
        middle = count // 2
        left = self.mergeKLists(lists[:middle])
        right = self.mergeKLists(lists[middle:])
        return self.mergeTwoLists(left, right)
```

**复杂度：** 时间 \(O((N+k)\log(k+1))\)，额外空间 \(O(k)\)；N 为总节点数，k 为链表数，计入数组切片成本。

**注意：** 复用节点，但递归切片会复制头节点引用。

#### 补充：从两两合并开始，逐轮加倍

先合并相邻两条链表，再合并相邻两组，组大小每轮翻倍。每组结果写回 `lists` 的组起点，下一轮直接取这些位置继续合并。

```python
class Solution:

    def mergeTwoLists(self, a, b):
        sentinel = ListNode()
        tail = sentinel
        while a and b:
            if a.val < b.val:
                tail.next = a
                a = a.next
            else:
                tail.next = b
                b = b.next
            tail = tail.next
        tail.next = a if a else b
        return sentinel.next

    def mergeKLists(self, lists):
        if not lists:
            return None
        width = 1
        while width < len(lists):
            for begin in range(0, len(lists) - width, width * 2):
                lists[begin] = self.mergeTwoLists(lists[begin], lists[begin + width])
            width *= 2
        return lists[0]
```

**复杂度：** 时间 \(O(k+N\log(k+1))\)，额外空间 \(O(1)\)；N 为总节点数，k 为链表数。

**注意：** 会重连输入节点，并改写 `lists` 中各组合并后的头指针。

**写法补充：** 堆中可以保存带比较规则的节点，也可以保存值、链表编号与节点组成的元组。

### LRU 缓存（LeetCode 146）

中等 · [力扣原题](https://leetcode.cn/problems/lru-cache/) · [灵茶山艾府题解](https://leetcode.cn/problems/lru-cache/solutions/2456294/tu-jie-yi-zhang-tu-miao-dong-lrupythonja-czgt/)

#### 题面

实现容量固定的 `LRUCache`。缓存保存键和值；容量满后再加入新键时，应删除最长时间没有被读取或更新的那个键。

`LRUCache(capacity)` 创建缓存；`get(key)` 返回已有值，不存在则返回 `-1`；`put(key,value)` 插入或更新。成功读取和写入都算一次使用。`get` 和 `put` 的平均时间复杂度都必须是 \(O(1)\)。

**数据范围与约定**

- `1 <= capacity <= 3000`
- `0 <= key <= 10000`
- `0 <= value <= 10^5`
- 最多调用 2 * 10^5 次 `get` 和 `put`

**示例**

容量为 `2`：写入 `(1,10)`、`(2,20)`，读取 `1` 后再写入 `(3,30)`，键 `2` 被淘汰，读取它返回 `-1`。

#### 解法：字典负责查找，双向链表记录使用顺序

字典把键映射到节点，让查找无需遍历。双向链表按最近使用顺序排列：读写一个键后，把它移到头部；超出容量时，删除尾部最久未用的节点，同时从字典删除该键。

`head`、`tail` 是不存实际数据的辅助节点，用来统一处理头尾连接。数据节点保存键和值，删除时才能同步更新字典。

```python
class _CacheNode:

    def __init__(self, key=0, value=0):
        self.key, self.value = (key, value)
        self.prev = self.next = None

class LRUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.items = {}
        self.head, self.tail = (_CacheNode(), _CacheNode())
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _front(self, node):
        node.prev, node.next = (self.head, self.head.next)
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.items:
            return -1
        node = self.items[key]
        self._remove(node)
        self._front(node)
        return node.value

    def put(self, key, value):
        if key in self.items:
            node = self.items[key]
            node.value = value
            self._remove(node)
        else:
            node = _CacheNode(key, value)
            self.items[key] = node
        self._front(node)
        if len(self.items) > self.capacity:
            expired = self.tail.prev
            self._remove(expired)
            del self.items[expired.key]
```

**复杂度：** 平均每次操作 \(O(1)\)，空间 \(O(C)\)；\(C\) 为缓存容量。

#### 补充：用 OrderedDict 维护访问顺序

`OrderedDict` 同时支持按键查询和调整键的顺序。约定最前面是最近使用的键，`get` 命中和 `put` 后都将键移到最前面；超过容量时删除末尾最久未使用的键。

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = OrderedDict()

    def get(self, key):
        if key not in self.entries:
            return -1
        self.entries.move_to_end(key, last=False)
        return self.entries[key]

    def put(self, key, value):
        self.entries[key] = value
        self.entries.move_to_end(key, last=False)
        if len(self.entries) > self.capacity:
            self.entries.popitem(last=True)
```

**复杂度：** get、put 平均时间 \(O(1)\)，空间 \(O(\text{capacity})\)。

**注意：** 标准库代替手写哈希表加双向链表；访问顺序规则相同。


## 二叉树

### 二叉树的中序遍历（LeetCode 94）

简单 · [力扣原题](https://leetcode.cn/problems/binary-tree-inorder-traversal/) · [灵茶山艾府题解](https://leetcode.cn/problems/binary-tree-inorder-traversal/solutions/3844031/tu-jie-morris-bian-li-xian-suo-er-cha-sh-cm2s/)

#### 题面

给定二叉树的根节点 `root`，按中序遍历的顺序返回所有节点值。中序的顺序是：先按同样规则遍历左子树，再读取当前节点，最后遍历右子树。

返回一个一维列表。输入为空树时返回空列表。

**数据范围与约定**

- `树中节点数目在范围 [0, 100] 内`
- `-100 <= Node.val <= 100`

**进阶要求**

- 递归算法很简单，你可以通过迭代算法完成吗？

**示例**

根为 `4`、左孩子 `2`、右孩子 `6`，中序结果为 `[2,4,6]`。

#### 解法：Morris 遍历：借用空指针返回父节点

当前节点有左子树时，找到左子树最右侧的节点。第一次到这里，把它原本为空的右指针临时指回当前节点，再进入左子树；沿这条连接返回时，拆除连接，读取当前值，然后进入右子树。

没有左子树时，直接读取当前值并向右走。临时连接代替了递归栈，结束时全部拆除，树结构恢复。

```python
class Solution:

    def inorderTraversal(self, root):
        answer = []
        current = root
        while current:
            if current.left is None:
                answer.append(current.val)
                current = current.right
                continue
            previous = current.left
            while previous.right and previous.right is not current:
                previous = previous.right
            if previous.right is None:
                previous.right = current
                current = current.left
            else:
                previous.right = None
                answer.append(current.val)
                current = current.right
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)，输出数组另计；\(n\) 为节点数。

#### 补充：递归中序遍历

先完整访问左子树，再记录当前节点，最后访问右子树。递归调用负责回到尚未处理的父节点，因此不需要临时修改树的指针。

```python
class Solution:
    def inorderTraversal(self, root):
        result = []
        def visit(node):
            if node is not None:
                visit(node.left)
                result.append(node.val)
                visit(node.right)
        visit(root)
        return result
```

**复杂度：** 时间 \(O(n)\)，除答案外递归栈 \(O(h)\)，h 为树高。

**注意：** 比 Morris 遍历直观，但最坏需要线性递归栈。

### 二叉树的最大深度（LeetCode 104）

简单 · [力扣原题](https://leetcode.cn/problems/maximum-depth-of-binary-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/maximum-depth-of-binary-tree/solutions/2010612/kan-wan-zhe-ge-shi-pin-rang-ni-dui-di-gu-44uz/)

#### 题面

给定二叉树根节点 `root`，找出从根节点到某个叶子节点的最长路径，返回这条路径上的节点个数，也就是树的最大深度。

叶子节点是没有左孩子和右孩子的节点。只有根节点时深度为 1，空树的深度为 0。

**数据范围与约定**

- `树中节点的数量在 [0, 10^4] 区间内。`
- `-100 <= Node.val <= 100`

**示例**

根 `1` 的左孩子是 `2`，`2` 的左孩子是 `3`，根的右孩子是 `4`。最长路径 `1→2→3` 有三个节点，返回 `3`。

#### 解法：左右子树深度的较大值加一

空树深度为零。对非空节点，递归求左右子树深度，取较大值再加一，计入当前节点。左右两边都用同样规则计算，因此根节点得到的就是整棵树的最大深度。

```python
class Solution:

    def maxDepth(self, root):

        def depth(node):
            if node is None:
                return 0
            return 1 + max(depth(node.left), depth(node.right))
        return depth(root)
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高，最坏 \(h=n\)。

#### 补充：从根向下传递当前深度

遍历参数记录到父节点为止的深度。进入当前节点后加一，更新最大值，再把新深度传给两个孩子。空树没有节点，最大深度保持为零。

```python
class Solution:
    def maxDepth(self, root):
        maximum = 0
        def visit(node, parent_depth):
            nonlocal maximum
            if node is None:
                return
            depth = parent_depth + 1
            maximum = max(maximum, depth)
            visit(node.left, depth)
            visit(node.right, depth)
        visit(root, 0)
        return maximum
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)。

**注意：** 与从子树返回高度的方法同阶，区别在于深度信息由上往下传递。

### 翻转二叉树（LeetCode 226）

简单 · [力扣原题](https://leetcode.cn/problems/invert-binary-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/invert-binary-tree/solutions/2713610/shi-pin-shen-ru-li-jie-di-gui-pythonjava-zhqh/)

#### 题面

给定二叉树根节点 `root`，把整棵树左右翻转，返回翻转后的根节点。具体来说，每个节点的左孩子和右孩子都要交换。

交换要发生在树的所有层，不只是根节点这一层。空树翻转后仍为空树。

**数据范围与约定**

- `树中节点数目范围在 [0, 100] 内`
- `-100 <= Node.val <= 100`

**示例**

`[1,2,3,4,null,null,5]` 翻转为 `[1,3,2,5,null,null,4]`。

#### 解法：先翻转子树，再交换左右孩子

递归把左右子树各自翻转，再交换它们在当前节点下的位置。空节点直接返回。每个节点都执行一次交换，因此所有层都会翻转。

```python
class Solution:

    def invertTree(self, root):
        if root is None:
            return None
        root.left, root.right = (self.invertTree(root.right), self.invertTree(root.left))
        return root
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

#### 补充：先交换孩子，再递归处理

每个节点先把左右孩子交换，再分别翻转交换后的两棵子树。当前层和后续各层都完成交换，整棵树便成为镜像。

```python
class Solution:
    def invertTree(self, root):
        if root is None:
            return None
        root.left, root.right = root.right, root.left
        self.invertTree(root.left)
        self.invertTree(root.right)
        return root
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)。

**注意：** 与先递归再交换的方法效率一致，只是处理顺序不同。

**写法补充：** 先递归后交换的两个版本，仅在临时变量与并行赋值上不同。先交换后递归的版本已另列。

### 对称二叉树（LeetCode 101）

简单 · [力扣原题](https://leetcode.cn/problems/symmetric-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/symmetric-tree/solutions/2015063/ru-he-ling-huo-yun-yong-di-gui-lai-kan-s-6dq5/)

#### 题面

给定二叉树根节点 `root`，判断树的左半部分和右半部分是否互为镜像，返回布尔值。

不仅对应节点的值要相同，节点是否存在的位置也必须对称。例如左边有一个左孩子，就要求镜像位置的右边有一个对应的右孩子。

**数据范围与约定**

- `树中节点数目在范围 [1, 1000] 内`
- `-100 <= Node.val <= 100`

**进阶要求**

- 你可以运用递归和迭代两种方法解决这个问题吗？

**示例**

`[1,2,2,3,4,4,3]` 对称；`[1,2,2,null,3,null,3]` 不对称，因为两个 `3` 没在镜像位置。

#### 解法：成对比较镜像位置

比较左右两棵子树：都为空时对称，只有一边为空或节点值不同就不对称。值相同时，再比较“左边的左孩子与右边的右孩子”，以及另一对相反方向的孩子；两组都对称才成立。

```python
class Solution:

    def isSymmetric(self, root):

        def mirror(a, b):
            if a is None or b is None:
                return a is b
            return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
        return root is None or mirror(root.left, root.right)
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

### 二叉树的直径（LeetCode 543）

简单 · [力扣原题](https://leetcode.cn/problems/diameter-of-binary-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/diameter-of-binary-tree/solutions/2227017/shi-pin-che-di-zhang-wo-zhi-jing-dpcong-taqma/)

#### 题面

给定二叉树根节点 `root`，找出任意两个节点之间最长的连接路径，返回这条路径经过的边数。这个长度称为二叉树的直径。

路径可以从任意节点开始、在任意节点结束，不一定经过根。一个节点组成的树没有边，因此直径为 0。

**数据范围与约定**

- `树中节点数目在范围 [1, 10^4] 内`
- `-100 <= Node.val <= 100`

**示例**

`[1,2,3,4,5]` 的最长路径可为 `4→2→1→3`，经过三条边，返回 `3`。

#### 解法：每个节点连接左右两条最长向下路径

递归向父节点返回当前子树的高度。在每个节点处，把左、右子树高度相加，得到经过这个节点的最长路径边数，用它更新答案。最长路径不一定经过根，所以每个节点都要检查一次。

```python
class Solution:

    def diameterOfBinaryTree(self, root):
        longest = 0

        def height(node):
            nonlocal longest
            if node is None:
                return 0
            left, right = (height(node.left), height(node.right))
            longest = max(longest, left + right)
            return max(left, right) + 1
        height(root)
        return longest
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

**写法补充：** 高度按边数或节点数表示均可，只需让初值和最后换算保持一致。

### 二叉树的层序遍历（LeetCode 102）

中等 · [力扣原题](https://leetcode.cn/problems/binary-tree-level-order-traversal/) · [灵茶山艾府题解](https://leetcode.cn/problems/binary-tree-level-order-traversal/solutions/2049807/bfs-wei-shi-yao-yao-yong-dui-lie-yi-ge-s-xlpz/)

#### 题面

给定二叉树根节点 `root`，从根所在的第一层开始，一层一层地读取节点，每层按从左到右的顺序读取。返回二维列表，每个子列表保存一层的节点值。

空树返回空列表。例如根为 1、左右孩子为 2 和 3 时，结果为 `[[1],[2,3]]`。

**数据范围与约定**

- `树中节点数目在范围 [0, 2000] 内`
- `-1000 <= Node.val <= 1000`

**示例**

`[1,2,3,null,4]` 返回 `[[1],[2,3],[4]]`，每个子列表对应一层。

#### 解法：队列按层读取

先把根放进队列。每轮开始时记下队列长度，这就是当前层的节点数；只取出这么多个节点，并按先左后右的顺序加入它们的孩子。新加入的节点留到下一轮处理，各层就不会混在一起。

```python
from collections import deque

class Solution:

    def levelOrder(self, root):
        if root is None:
            return []
        queue = deque([root])
        answer = []
        while queue:
            layer = []
            for _ in range(len(queue)):
                node = queue.popleft()
                layer.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            answer.append(layer)
        return answer
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(w)\)，输出另计；\(n\) 为节点数，\(w\) 为最大层宽，最坏 \(O(n)\)。

#### 补充：用两个数组分开保存相邻两层

`current` 只保存当前层，从左到右记录其值，并把孩子按先左后右加入 `following`。当前层处理完后，`following` 整体成为下一层，天然不会混淆层的边界。

```python
class Solution:
    def levelOrder(self, root):
        if root is None:
            return []
        answer, current = [], [root]
        while current:
            values, following = [], []
            for node in current:
                values.append(node.val)
                if node.left:
                    following.append(node.left)
                if node.right:
                    following.append(node.right)
            answer.append(values)
            current = following
        return answer
```

**复杂度：** 时间 \(O(n)\)，除答案外空间 \(O(w)\)，w 为最大层宽。

### 将有序数组转换为二叉搜索树（LeetCode 108）

简单 · [力扣原题](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/solutions/2927064/ru-men-di-gui-cong-er-cha-shu-kai-shi-py-inu6/)

#### 题面

给定严格递增的数组 `nums`，用其中全部元素构造一棵高度平衡的二叉搜索树，返回树的根节点。

二叉搜索树要求每个节点左子树的所有值小于它、右子树的所有值大于它。高度平衡要求每个节点左右子树的高度差不超过 1；符合条件的树可能不止一种，返回任意一种即可。

**数据范围与约定**

- `1 <= nums.length <= 10^4`
- `-10^4 <= nums[i] <= 10^4`
- `nums` 按 严格递增 顺序排列

**示例**

`[-2,0,3,5,8]` 可构造成 `[3,0,8,-2,null,5]`：根为 `3`，两侧都满足大小关系和高度要求。

#### 解法：每次取中间元素作为根

有序数组的中间元素作为根，左边构造左子树，右边构造右子树。两边元素个数至多相差一，对每段重复这个操作即可得到平衡树。递归传下标范围，不复制子数组。

```python
class Solution:

    def sortedArrayToBST(self, nums):

        def build(left, right):
            if left == right:
                return None
            middle = (left + right) // 2
            node = TreeNode(nums[middle])
            node.left = build(left, middle)
            node.right = build(middle + 1, right)
            return node
        return build(0, len(nums))
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(\log n)\)，输出树另计；\(n\) 为数组长度。

#### 补充：切出左右半段递归建树

有序数组的中间值作为根，左半段建左子树，右半段建右子树。两边长度至多相差一，因此每层都保持高度平衡。

```python
class Solution:
    def sortedArrayToBST(self, nums):
        if not nums:
            return None
        middle = len(nums) // 2
        left = self.sortedArrayToBST(nums[:middle])
        right = self.sortedArrayToBST(nums[middle + 1:])
        return TreeNode(nums[middle], left, right)
```

**复杂度：** 时间 \(O(n \log n)\)，除输出树外辅助空间 \(O(n)\)，包含活动中的切片。

**注意：** 切片会复制元素；主解法传下标范围，避免复制。

### 验证二叉搜索树（LeetCode 98）

中等 · [力扣原题](https://leetcode.cn/problems/validate-binary-search-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/validate-binary-search-tree/solutions/2020306/qian-xu-zhong-xu-hou-xu-san-chong-fang-f-yxvh/)

#### 题面

给定二叉树根节点 `root`，判断它是否是一棵合法的二叉搜索树，返回布尔值。对树中的每个节点，都要同时满足：左子树的所有值比它小，右子树的所有值比它大。

比较的是整棵左右子树，不只是直接相连的两个孩子。大小关系必须严格成立，所以出现相同值也可能使树不合法。

**数据范围与约定**

- `树中节点数目范围在 [1, 10^4] 内`
- `-2^31 <= Node.val <= 2^31 - 1`

**示例**

`[5,2,8,null,null,4,9]` 返回 `False`。节点 `4` 位于根 `5` 的右子树，必须大于 `5`。

#### 解法：递归传递允许的值范围

`low`、`high` 是当前节点必须严格处于其间的上下界。进入左子树时，把上界改为当前值；进入右子树时，把下界改为当前值。其余边界继续保留，确保每个节点也满足所有祖先的限制。

```python
class Solution:

    def isValidBST(self, root):

        def valid(node, low, high):
            if node is None:
                return True
            if not low < node.val < high:
                return False
            return valid(node.left, low, node.val) and valid(node.right, node.val, high)
        return valid(root, float('-inf'), float('inf'))
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

#### 补充：中序访问必须严格递增

二叉搜索树的中序顺序应严格递增。遍历时只保存上一个访问值，一旦当前值不大于它就失败；先检查左子树，再检查当前值，最后检查右子树。

```python
from math import inf

class Solution:
    def isValidBST(self, root):
        previous = -inf
        def visit(node):
            nonlocal previous
            if node is None:
                return True
            if not visit(node.left) or node.val <= previous:
                return False
            previous = node.val
            return visit(node.right)
        return visit(root)
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)。

**注意：** 严格大于会排除重复值；不能只比较节点与它的直接孩子。

#### 补充：后序返回子树最小值和最大值

递归取得左右子树的最小值、最大值。当前值大于左侧最大值、又小于右侧最小值，才能返回整棵子树的范围。空树返回 `(inf,-inf)`，不限制父节点；非法子树返回 `(-inf,inf)`，让父节点也无法通过检查。

```python
from math import inf

class Solution:
    def isValidBST(self, root):
        def bounds(node):
            if node is None:
                return inf, -inf
            low_left, high_left = bounds(node.left)
            low_right, high_right = bounds(node.right)
            if not high_left < node.val < low_right:
                return -inf, inf
            return min(low_left, node.val), max(high_right, node.val)
        return bounds(root)[1] != inf
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)。

**注意：** 与传入上下界的方法方向相反：这里把子树范围向父节点汇总。

### 二叉搜索树中第 K 小的元素（LeetCode 230）

中等 · [力扣原题](https://leetcode.cn/problems/kth-smallest-element-in-a-bst/) · [灵茶山艾府题解](https://leetcode.cn/problems/kth-smallest-element-in-a-bst/solutions/2952810/zhong-xu-bian-li-pythonjavaccgojsrust-by-wc02/)

#### 题面

给定一棵合法二叉搜索树的根节点 `root` 和整数 `k`，返回树中第 `k` 小的节点值。也就是把所有节点值按从小到大排列后，取第 `k` 个。

`k` 从 1 开始计数，题目保证它不超过节点总数。返回节点值，不需要返回节点对象或排序后的整个列表。

**数据范围与约定**

- 树中的节点数为 n 。
- `1 <= k <= n <= 10^4`
- `0 <= Node.val <= 10^4`

**进阶要求**

- 如果二叉搜索树经常被修改（插入/删除操作）并且你需要频繁地查找第 `k` 小的值，你将如何优化算法？

**示例**

`root=[5,2,8,1,3]`、`k=3`，返回 `3`；升序为 `1,2,3,5,8`。

#### 解法：中序访问到第 k 个就返回

二叉搜索树按“左子树、当前节点、右子树”访问，得到的就是升序。每次真正读取当前值时把 `k` 减一，降到零即找到答案。用递归返回值逐层传回答案，跳过尚未访问的部分。

```python
class Solution:

    def kthSmallest(self, root, k):
        remaining = k

        def visit(node):
            nonlocal remaining
            if node is None:
                return None
            found = visit(node.left)
            if found is not None:
                return found
            remaining -= 1
            if remaining == 0:
                return node.val
            return visit(node.right)
        return visit(root)
```

**复杂度：** 时间 \(O(h+k)\)，最坏 \(O(n)\)；递归栈 \(O(h)\)。\(n\) 为节点数，\(h\) 为树高。

#### 补充：中序计数，在外部记录答案

每访问一个节点便把剩余名次减一，恰好降到零时记录节点值。后续递归入口发现名次已非正便停止展开；已在调用栈中的祖先仍会返回，但不会覆盖答案。

```python
class Solution:
    def kthSmallest(self, root, k):
        answer = 0
        def visit(node):
            nonlocal k, answer
            if node is None or k <= 0:
                return
            visit(node.left)
            k -= 1
            if k == 0:
                answer = node.val
            visit(node.right)
        visit(root)
        return answer
```

**复杂度：** 最坏时间 \(O(n)\)，更细为 \(O(h+k)\)，递归栈 \(O(h)\)。

**注意：** 答案保存在递归外部；另一个版本通过返回值传回答案。

### 二叉树的右视图（LeetCode 199）

中等 · [力扣原题](https://leetcode.cn/problems/binary-tree-right-side-view/) · [灵茶山艾府题解](https://leetcode.cn/problems/binary-tree-right-side-view/solutions/2015061/ru-he-ling-huo-yun-yong-di-gui-lai-kan-s-r1nc/)

#### 题面

给定二叉树根节点 `root`，想象站在树的右侧观察它，返回从上到下能看到的节点值。每一层取该层实际存在的最右节点。

如果某层在右子树中没有节点，左子树更深处的节点也可能被看到。空树返回空列表。

**数据范围与约定**

- `二叉树的节点个数的范围是 [0,100]`
- `-100 <= Node.val <= 100`

**示例**

`[1,2,3,null,4]` 的右视图为 `[1,3,4]`；第三层只有来自左子树的节点 `4`。

#### 解法：先右后左，每层只记第一次

递归时先访问右子树，再访问左子树。这样每层第一次遇到的节点，就是该层最右节点，把它记入答案。左子树仍要遍历，因为它可能比右子树更深。

```python
class Solution:

    def rightSideView(self, root):
        answer = []

        def visit(node, depth):
            if node is None:
                return
            if depth == len(answer):
                answer.append(node.val)
            visit(node.right, depth + 1)
            visit(node.left, depth + 1)
        visit(root, 0)
        return answer
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)，输出另计；\(n\) 为节点数，\(h\) 为树高。

#### 补充：按层遍历，每层取最右节点

每层数组按从左到右排列，最后一个节点就是这一层从右边能看到的节点。构造下一层时也按先左孩子、后右孩子加入，维持同样的顺序。

```python
class Solution:
    def rightSideView(self, root):
        if root is None:
            return []
        answer, layer = [], [root]
        while layer:
            answer.append(layer[-1].val)
            following = []
            for node in layer:
                if node.left:
                    following.append(node.left)
                if node.right:
                    following.append(node.right)
            layer = following
        return answer
```

**复杂度：** 时间 \(O(n)\)，除答案外空间 \(O(w)\)，w 为最大层宽。

**注意：** 保存一层节点；先右后左的递归方法保存一条访问路径。

### 二叉树展开为链表（LeetCode 114）

中等 · [力扣原题](https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/) · [灵茶山艾府题解](https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/solutions/2992172/liang-chong-fang-fa-tou-cha-fa-fen-zhi-p-h9bg/)

#### 题面

给定二叉树根节点 `root`，调整节点连接，把整棵树展开成一条链。沿链读取节点的顺序必须与原树的先序遍历相同：先当前节点，再左子树，最后右子树。

继续使用 `TreeNode` 节点：`right` 指向链上的下一个节点，所有 `left` 都置为 `None`。直接修改输入树，不需要返回另一条链表。

**数据范围与约定**

- `树中结点数在范围 [0, 2000] 内`
- `-100 <= Node.val <= 100`

**进阶要求**

- 你可以使用原地算法（ \(O(1)\) 额外空间）展开这棵树吗？

**示例**

`[1,2,5,3,4,null,6]` 展开后沿 `right` 依次是 `1→2→3→4→5→6`，所有 `left` 均为空。

#### 解法：逆序访问，再插到链头

需要的顺序是“根、左、右”。因此按相反的“右、左、根”顺序递归，每处理一个节点，就让它的 `right` 指向已经建好的链头，清空 `left`，再更新链头。不断往前插入，最终恰好得到先序顺序。

```python
class Solution:

    def flatten(self, root):
        front = None

        def visit(node):
            nonlocal front
            if node is None:
                return
            visit(node.right)
            visit(node.left)
            node.right = front
            node.left = None
            front = node
        visit(root)
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

**注意：** 使用原树节点；递归栈仍占空间，未达到常数额外空间的进阶目标。

#### 补充：递归展开两棵子树，并返回尾节点

先把左右子树分别展开，得到各自尾节点。若有左链，就让左链尾接右链头，再把整条左链接到根的 `right`，清空根的 `left`。返回最末尾节点，父节点便无需再次扫描链尾。

```python
class Solution:
    def flatten(self, root):
        if root is None:
            return None
        left_tail = self.flatten(root.left)
        right_tail = self.flatten(root.right)
        if left_tail:
            left_tail.right = root.right
            root.right = root.left
            root.left = None
        return right_tail or left_tail or root
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)。

**注意：** 返回尾节点供递归内部连接使用；LeetCode 仍检查原树上的修改。

### 从前序与中序遍历序列构造二叉树（LeetCode 105）

中等 · [力扣原题](https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) · [灵茶山艾府题解](https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/solutions/2646359/tu-jie-cong-on2-dao-onpythonjavacgojsrus-aob8/)

#### 题面

给定两个数组 `preorder` 和 `inorder`，分别记录同一棵二叉树的前序和中序遍历结果。根据这两个数组还原二叉树，返回根节点。

前序是当前节点、左子树、右子树；中序是左子树、当前节点、右子树。题目保证两个数组有效、包含相同节点值，而且节点值互不相同。

**数据范围与约定**

- `1 <= preorder.length <= 3000`
- `inorder.length == preorder.length`
- `-3000 <= preorder[i], inorder[i] <= 3000`
- `preorder` 和 `inorder` 均 无重复 元素
- `inorder` 均出现在 `preorder`
- `preorder` 保证 为二叉树的前序遍历序列
- `inorder` 保证 为二叉树的中序遍历序列

**示例**

前序 `[4,2,1,3,6]`、中序 `[1,2,3,4,6]`，可还原为 `[4,2,6,1,3]`。

#### 解法：前序定根，中序划分左右子树

前序的第一项是根。在中序中找到根，左侧元素属于左子树，右侧属于右子树；左侧数量又能确定前序中两棵子树各占多少项。递归处理这些区间，并预先用字典记录中序下标，避免反复查找。

```python
class Solution:

    def buildTree(self, preorder, inorder):
        positions = {value: i for i, value in enumerate(inorder)}

        def build(pre_start, in_start, size):
            if size == 0:
                return None
            value = preorder[pre_start]
            pivot = positions[value]
            left_size = pivot - in_start
            node = TreeNode(value)
            node.left = build(pre_start + 1, in_start, left_size)
            node.right = build(pre_start + 1 + left_size, pivot + 1, size - left_size - 1)
            return node
        return build(0, 0, len(preorder))
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)，含哈希表和递归栈，不计返回树；\(n\) 为节点数。

#### 补充：查找根的位置，再切片递归

前序第一个数是根。在中序中找到它后，左边元素数量就是左子树大小，据此切开前序和中序，递归构造左右子树。

```python
class Solution:
    def buildTree(self, preorder, inorder):
        if not preorder:
            return None
        root_value = preorder[0]
        left_count = inorder.index(root_value)
        left = self.buildTree(preorder[1:left_count + 1], inorder[:left_count])
        right = self.buildTree(preorder[left_count + 1:], inorder[left_count + 1:])
        return TreeNode(root_value, left, right)
```

**复杂度：** 最坏时间 \(O(n^2)\)，除输出树外最坏空间 \(O(n^2)\)，来自退化树递归期间保留的多层切片。

**注意：** 更直观；主解法用下标表和区间边界，避免重复查找及切片。

### 路径总和 III（LeetCode 437）

中等 · [力扣原题](https://leetcode.cn/problems/path-sum-iii/) · [灵茶山艾府题解](https://leetcode.cn/problems/path-sum-iii/solutions/2784856/zuo-fa-he-560-ti-shi-yi-yang-de-pythonja-fmzo/)

#### 题面

给定二叉树根节点 `root` 和整数 `targetSum`，统计树中有多少条路径的节点值总和等于 `targetSum`。

路径必须沿父节点到孩子的方向连续向下，不能向上走，但起点不必是根、终点不必是叶子。路径不能为空，单个节点也算一条路径；返回符合条件的路径条数。

**数据范围与约定**

- `二叉树的节点个数的范围是 [0,1000]`
- `-10^9 <= Node.val <= 10^9`
- `-1000 <= targetSum <= 1000`

**示例**

根为 `1`、左右孩子为 `2` 和 `3`，`targetSum=3`，返回 `2`：合法路径是 `1→2` 和单节点 `3`。

#### 解法：当前根路径的前缀和计数

从根向下累计节点值，得到 `prefix`。当前路径中，每个曾出现的 `prefix-targetSum` 都对应一条以当前节点结尾的合法路径；用字典记录出现次数。先查询，再加入当前累计和。

离开当前节点时撤销这一次记录，让字典只保留当前分支，避免把不同分支拼成一条路径。

```python
class Solution:

    def pathSum(self, root, targetSum):
        counts = {0: 1}

        def visit(node, prefix):
            if node is None:
                return 0
            prefix += node.val
            result = counts.get(prefix - targetSum, 0)
            counts[prefix] = counts.get(prefix, 0) + 1
            result += visit(node.left, prefix) + visit(node.right, prefix)
            counts[prefix] -= 1
            return result
        return visit(root, 0)
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(n)\)，含前缀频次表和递归栈；\(n\) 为节点数。

### 二叉树的最近公共祖先（LeetCode 236）

中等 · [力扣原题](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/solutions/2023872/fen-lei-tao-lun-luan-ru-ma-yi-ge-shi-pin-2r95/)

#### 题面

给定二叉树根节点 `root` 及其中两个不同节点 `p`、`q`，返回它们最近的公共祖先节点。这个节点既能沿向下的路径到达 `p`，也能到达 `q`，并且在所有满足条件的节点中位置最深。

一个节点也可以是它自身的祖先，所以答案可能就是 `p` 或 `q`。题目保证两个目标节点都在树中，返回节点对象。

**数据范围与约定**

- `树中节点数目在范围 [2, 10^5] 内。`
- `-10^9 <= Node.val <= 10^9`
- 所有 Node.val 互不相同 。
- `p != q`
- `p` 和 `q` 均存在于给定的二叉树中。

**示例**

根 `5` 的左孩子 `2` 有孩子 `1、3`，右孩子是 `8`。节点 `1、3` 的最近公共祖先是 `2`；节点 `1、8` 的是 `5`。

#### 解法：看两个目标分别出现在哪一侧

遇到空节点返回空，遇到 `p` 或 `q` 返回该节点。否则递归查左右子树：两侧都返回非空，说明两个目标在两边，当前节点就是最近公共祖先；只有一侧非空，就把那一侧的结果继续向上传。

```python
class Solution:

    def lowestCommonAncestor(self, root, p, q):
        if root is None or root is p or root is q:
            return root
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left and right:
            return root
        return left or right
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

### 二叉树中的最大路径和（LeetCode 124）

困难 · [力扣原题](https://leetcode.cn/problems/binary-tree-maximum-path-sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/binary-tree-maximum-path-sum/solutions/2227021/shi-pin-che-di-zhang-wo-zhi-jing-dpcong-n9s91/)

#### 题面

给定二叉树根节点 `root`，在树中选择一条非空路径，使路径上的节点值总和最大，返回这个最大和。

路径中相邻节点必须有父子连接，同一个节点不能重复经过。路径可以先向上再向下，不必经过根，也不必从根走到叶子；只选一个节点也合法。

**数据范围与约定**

- `树中节点数目范围是 [1, 3 * 10^4]`
- `-1000 <= Node.val <= 1000`

**示例**

`[-8,4,10,null,null,7,3]` 返回 `20`，最大路径是 `7→10→3`。

#### 解法：向上只接一边，计算答案时可接两边

递归求左右子树能提供的最大向下路径和，负数按零处理，表示不接这一边。经过当前节点的候选答案可以同时接左右两边；但返回父节点时只能选较大的一边，否则会出现分叉，不能成为一条路径。

```python
class Solution:

    def maxPathSum(self, root):
        best = float('-inf')

        def chain(node):
            nonlocal best
            if node is None:
                return 0
            left = max(0, chain(node.left))
            right = max(0, chain(node.right))
            best = max(best, node.val + left + right)
            return node.val + max(left, right)
        chain(root)
        return best
```

**复杂度：** 时间 \(O(n)\)，递归栈 \(O(h)\)；\(n\) 为节点数，\(h\) 为树高。

**注意：** 路径必须非空；全为负数时，答案是最大的单个节点值。


## 图论

### 岛屿数量（LeetCode 200）

中等 · [力扣原题](https://leetcode.cn/problems/number-of-islands/) · [灵茶山艾府题解](https://leetcode.cn/problems/number-of-islands/solutions/2965773/ba-fang-wen-guo-de-ge-zi-cha-shang-qi-zi-9gs0/)

#### 题面

给定由字符 `'1'` 和 `'0'` 组成的二维网格 `grid`，其中 `'1'` 表示陆地、`'0'` 表示水，返回岛屿的数量。

能通过上下左右相邻陆地连接在一起的所有格子，算同一座岛；仅斜角相邻不算连接。网格外部都视为水。

**数据范围与约定**

- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 300`
- `grid[i][j] 的值为 '0' 或 '1'`

**示例**

`[["1","1","0"],["0","1","0"],["1","0","1"]]` 有三座岛：左上三格连成一座，底部两格各是一座。

#### 解法：遇到新陆地，标记整座岛

扫描网格，遇到未访问的陆地就把岛屿数加一，再沿上下左右递归访问与它相连的全部陆地。访问一个格子时先改成 `'2'`，防止从邻居绕回来重复访问。继续扫描时，已标记的岛不会再被计数。

```python
class Solution:

    def numIslands(self, grid):
        rows, cols = (len(grid), len(grid[0]))

        def search(row, col):
            if not 0 <= row < rows or not 0 <= col < cols:
                return
            if grid[row][col] != '1':
                return
            grid[row][col] = '2'
            search(row, col - 1)
            search(row, col + 1)
            search(row - 1, col)
            search(row + 1, col)
        answer = 0
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == '1':
                    search(row, col)
                    answer += 1
        return answer
```

**复杂度：** 时间 \(O(mn)\)，递归栈最坏占 \(O(mn)\)；\(m,n\) 为网格行列数。

**注意：** 会把输入中访问过的 `'1'` 改成 `'2'`。

### 腐烂的橘子（LeetCode 994）

中等 · [力扣原题](https://leetcode.cn/problems/rotting-oranges/) · [灵茶山艾府题解](https://leetcode.cn/problems/rotting-oranges/solutions/2773461/duo-yuan-bfsfu-ti-dan-pythonjavacgojsrus-yfmh/)

#### 题面

给定网格 `grid`，数值 `0` 表示空格，`1` 表示新鲜橘子，`2` 表示腐烂橘子。每过一分钟，腐烂橘子会让上下左右相邻的新鲜橘子也腐烂。求所有新鲜橘子都腐烂所需的最少分钟数。

所有腐烂源同时传播。如果存在永远无法腐烂的新鲜橘子，返回 `-1`；如果一开始就没有新鲜橘子，返回 0。

**数据范围与约定**

- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 10`
- `grid[i][j] 仅为 0 、 1 或 2`

**示例**

`[[2,1,1],[0,1,1]]` 返回 `3`，最远的右下角橘子在第三分钟腐烂。

#### 解法：所有腐烂橘子同时逐层传播

把初始腐烂橘子全部放入当前层，同时统计新鲜橘子数。每轮只处理当前层，将这一分钟新腐烂的橘子收集到下一层。处理完一层才增加时间，保证新腐烂的橘子下一分钟才能继续传播。结束后若仍有新鲜橘子，返回 `-1`。

```python
class Solution:

    def orangesRotting(self, grid):
        rows, cols = (len(grid), len(grid[0]))
        fresh = 0
        frontier = []
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == 1:
                    fresh += 1
                elif grid[row][col] == 2:
                    frontier.append((row, col))
        minutes = 0
        while frontier and fresh:
            minutes += 1
            current_layer = frontier
            frontier = []
            for row, col in current_layer:
                for next_row, next_col in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
                    if 0 <= next_row < rows and 0 <= next_col < cols and (grid[next_row][next_col] == 1):
                        grid[next_row][next_col] = 2
                        fresh -= 1
                        frontier.append((next_row, next_col))
        return minutes if fresh == 0 else -1
```

**复杂度：** 时间 \(O(mn)\)，队列空间 \(O(mn)\)；\(m,n\) 为网格行列数。

**注意：** 会把输入中新腐烂的橘子改成 `2`。

### 课程表（LeetCode 207）

中等 · [力扣原题](https://leetcode.cn/problems/course-schedule/) · [灵茶山艾府题解](https://leetcode.cn/problems/course-schedule/solutions/2992884/san-se-biao-ji-fa-pythonjavacgojsrust-by-pll7/)

#### 题面

共有 `numCourses` 门课程，编号从 0 到 `numCourses-1`。给定列表 `prerequisites`，其中 `[a,b]` 表示必须先完成课程 `b`，才能学习课程 `a`。判断是否能够完成全部课程。

可以自行安排课程顺序，但必须遵守所有先修关系。能完成返回 `True`，否则返回 `False`；不需要返回具体学习顺序。

**数据范围与约定**

- `1 <= numCourses <= 2000`
- `0 <= prerequisites.length <= 5000`
- `prerequisites[i].length == 2`
- `0 <= a_i, b_i < numCourses`
- `prerequisites[i] 中的所有课程对 互不相同`

**示例**

三门课的先修关系为 `[[1,0],[2,1]]` 时可以完成；再加入 `[0,2]` 就互相等待，返回 `False`。

#### 解法：区分未访问、检查中、已完成

沿课程依赖关系递归检查，用三种标记区分未访问、当前递归链中、已经检查完。若再次遇到当前链中的课程，就形成循环依赖，无法完成。已检查完的课程可直接跳过；所有课程都检查后仍无环，就能完成。

```python
class Solution:

    def canFinish(self, numCourses, prerequisites):
        graph = [[] for _ in range(numCourses)]
        for course, previous in prerequisites:
            graph[previous].append(course)
        color = [0] * numCourses

        def visit(course):
            if color[course] == 1:
                return False
            if color[course] == 2:
                return True
            color[course] = 1
            for following in graph[course]:
                if not visit(following):
                    return False
            color[course] = 2
            return True
        return all((visit(course) for course in range(numCourses)))
```

**复杂度：** 时间及空间 \(O(n+m)\)，含图、状态和递归栈；\(n\) 为课程数，\(m\) 为依赖数。

### 实现 Trie (前缀树)（LeetCode 208）

中等 · [力扣原题](https://leetcode.cn/problems/implement-trie-prefix-tree/) · [灵茶山艾府题解](https://leetcode.cn/problems/implement-trie-prefix-tree/solutions/2993894/cong-er-cha-shu-dao-er-shi-liu-cha-shu-p-xsj4/)

#### 题面

实现前缀树 `Trie`，用于保存单词，并查询某个完整单词或某个前缀是否出现过。前缀是字符串开头连续的一段，例如 `app` 是 `apple` 的前缀。

`Trie()` 创建空结构；`insert(word)` 插入单词；`search(word)` 判断是否插入过这个完整单词；`startsWith(prefix)` 判断是否有已插入单词以此前缀开头。只有较长单词存在，不代表它的短前缀也被作为完整单词插入过。

**数据范围与约定**

- `1 <= word.length, prefix.length <= 2000`
- `word` 和 `prefix` 仅由小写英文字母组成
- `insert` 、 `search` 和 `startsWith` 调用次数 总计 不超过 3 * 10^4 次

**示例**

插入 `"cat"` 后，`search("cat")` 为 `True`，`search("ca")` 为 `False`，`startsWith("ca")` 为 `True`。

#### 解法：共享前缀路径，单独标记单词结尾

每个节点用字典保存下一字母对应的孩子。插入时按字母向下走，缺少节点就创建，最后标记单词结束。查询前缀只需整条路径存在；查询完整单词还必须检查结束标记，避免把较长单词的前缀误当成已插入单词。

```python
class Trie:

    def __init__(self):
        self.children = {}
        self.is_word = False

    def insert(self, word):
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = Trie()
            node = node.children[char]
        node.is_word = True

    def _walk(self, text):
        node = self
        for char in text:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_word

    def startsWith(self, prefix):
        return self._walk(prefix) is not None
```

**复杂度：** 固定二十六字母时，单次操作时间 \(O(L)\)，总空间 \(O(S)\)；\(L\) 为查询或插入长度，\(S\) 为所有插入字符串总长度。

#### 补充：每个节点用长度 26 的数组保存孩子

每走过一个字母就沿对应的数组下标前进，没有节点时按需创建。结束标记区分完整单词和仅有同样前缀：路径存在只说明前缀存在，`search` 还要检查结束标记。

```python
class TrieNode:
    __slots__ = ('children', 'terminal')
    def __init__(self):
        self.children = [None] * 26
        self.terminal = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            index = ord(char) - ord('a')
            if node.children[index] is None:
                node.children[index] = TrieNode()
            node = node.children[index]
        node.terminal = True

    def find(self, word):
        node = self.root
        for char in word:
            node = node.children[ord(char) - ord('a')]
            if node is None:
                return 0
        return 2 if node.terminal else 1

    def search(self, word):
        return self.find(word) == 2

    def startsWith(self, prefix):
        return self.find(prefix) != 0
```

**复杂度：** 单次操作时间 \(O(L)\)，L 为查询串长度；空间 \(O(26P)\)，P 为所有插入单词的不同前缀数。

**注意：** 字母范围固定为小写英文字母；与字典孩子表相比，这里每个节点固定分配 26 个位置。


## 回溯

### 全排列（LeetCode 46）

中等 · [力扣原题](https://leetcode.cn/problems/permutations/) · [灵茶山艾府题解](https://leetcode.cn/problems/permutations/solutions/2079585/hui-su-bu-hui-xie-tao-lu-zai-ci-jing-que-6hrh/)

#### 题面

给定元素互不相同的整数数组 `nums`，返回把这些元素重新排列后能够得到的所有不同排列。

每个排列必须包含全部元素，而且每个元素恰好使用一次。不同排列之间的输出顺序不限。

**数据范围与约定**

- `1 <= nums.length <= 6`
- `-10 <= nums[i] <= 10`
- `nums` 中的所有整数 互不相同

**示例**

`[1,2,4]` 共有六个排列：以 `1`、`2`、`4` 开头时，各有两种后续顺序。

#### 解法：逐位选择尚未使用的元素

预先分配定长 `path`，递归填写每个位置。选择一个尚未使用的元素，写入当前位置并标记使用，再填写下一位；返回时撤销标记。填满后复制整条路径加入答案，下一分支会直接覆盖对应位置，不必删除路径元素。

```python
class Solution:

    def permute(self, nums):
        size = len(nums)
        path = [0] * size
        used = [False] * size
        answer = []

        def search(position):
            if position == size:
                answer.append(path.copy())
                return
            for index in range(size):
                if not used[index]:
                    path[position] = nums[index]
                    used[index] = True
                    search(position + 1)
                    used[index] = False
        search(0)
        return answer
```

**复杂度：** 时间 \(O(n\cdot n!)\)，辅助空间 \(O(n)\)，输出空间 \(O(n\cdot n!)\)；\(n\) 为数组长度。

#### 补充：用剩余数字集合递归

`path` 固定长度，每层填一个位置。选中 `value` 后，下一层收到删去它的新集合；位置填满时复制 `path`。集合的遍历顺序不影响答案集合。

```python
class Solution:
    def permute(self, nums):
        path = [0] * len(nums)
        answer = []
        def fill(position, remain):
            if position == len(nums):
                answer.append(path.copy())
                return
            for value in remain:
                path[position] = value
                fill(position + 1, remain - {value})
        fill(0, set(nums))
        return answer
```

**复杂度：** 时间 \(O(n\cdot n!)\)，除答案外空间 \(O(n^2)\)，包含递归路径上同时存在的剩余集合。

**注意：** 每层创建新的剩余集合，因此比使用标记数组多用空间。

### 子集（LeetCode 78）

中等 · [力扣原题](https://leetcode.cn/problems/subsets/) · [灵茶山艾府题解](https://leetcode.cn/problems/subsets/solutions/2059409/hui-su-bu-hui-xie-tao-lu-zai-ci-pythonja-8tkl/)

#### 题面

给定元素互不相同的整数数组 `nums`，返回它的所有子集。一个子集可以选择其中任意几个元素，也可以一个都不选。

必须包含空集和全集，不能重复返回同一子集。子集只关心选中了哪些元素，不把元素的不同排列算作不同子集；答案顺序不限。

**数据范围与约定**

- `1 <= nums.length <= 10`
- `-10 <= nums[i] <= 10`
- `nums` 中的所有元素 互不相同

**示例**

`[2,5]` 的所有子集是 `[]、[2]、[5]、[2,5]`。

#### 解法：每个元素选择取或不取

按下标递归处理元素，每一步分为选当前数、不选当前数两种情况。处理完所有元素时，复制已选列表加入答案。固定处理顺序使每个子集只出现一次；全部不选就得到空集。

```python
class Solution:

    def subsets(self, nums):
        answer = []
        path = []

        def search(i):
            if i == len(nums):
                answer.append(path.copy())
                return
            search(i + 1)
            path.append(nums[i])
            search(i + 1)
            path.pop()
        search(0)
        return answer
```

**复杂度：** 时间 \(O(n2^n)\)，辅助空间 \(O(n)\)，输出空间 \(O(n2^n)\)；\(n\) 为数组长度。

#### 补充：枚举下一个选择的位置

当前 `path` 已经是一个子集，进入递归就保存。再从 `start` 起枚举下一个元素，递归只考虑其右边的位置，保证同一子集只按下标递增顺序出现一次。

```python
class Solution:
    def subsets(self, nums):
        answer, path = [], []
        def choose(start):
            answer.append(path.copy())
            for pos in range(start, len(nums)):
                path.append(nums[pos])
                choose(pos + 1)
                path.pop()
        choose(0)
        return answer
```

**复杂度：** 时间 \(O(n\cdot 2^n)\)，除答案外空间 \(O(n)\)。

#### 补充：二进制枚举所有选择

掩码的第 j 位表示是否选择 `nums[j]`。枚举全部 n 位二进制数，就得到每个位置选或不选的全部组合。

```python
class Solution:
    def subsets(self, nums):
        answer = []
        for mask in range(1 << len(nums)):
            subset = []
            for pos, value in enumerate(nums):
                if (mask >> pos) & 1:
                    subset.append(value)
            answer.append(subset)
        return answer
```

**复杂度：** 时间 \(O(n\cdot 2^n)\)，除答案及正在生成的子集外额外空间 \(O(1)\)，按本题小整数模型计。

### 电话号码的字母组合（LeetCode 17）

中等 · [力扣原题](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/) · [灵茶山艾府题解](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/solutions/2059416/hui-su-bu-hui-xie-tao-lu-zai-ci-pythonja-3orv/)

#### 题面

给定仅包含数字字符 `2` 到 `9` 的字符串 `digits`。每个数字可以替换成电话按键上的一个字母，返回逐位替换后能够组成的所有字符串。

映射关系是 `2→abc`、`3→def`、`4→ghi`、`5→jkl`、`6→mno`、`7→pqrs`、`8→tuv`、`9→wxyz`。每位数字选一个字母，数字的先后顺序不变；答案顺序不限。

**数据范围与约定**

- `1 <= digits.length <= 4`
- `digits[i] 是范围 ['2', '9'] 的一个数字。`

**示例**

`digits="27"` 有 `3×4=12` 种结果，包括 `"ap"、"aq"、"bp"、"cs"`。

#### 解法：逐位填写当前按键的字母

每个数字对应结果中的一个位置。先分配定长字符列表，递归时枚举当前按键上的字母，写入这一位后继续下一位。填满就连接成字符串；返回后下一分支直接覆盖当前位置。

```python
DIGIT_LETTERS = ('', '', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqrs', 'tuv', 'wxyz')

class Solution:

    def letterCombinations(self, digits):
        size = len(digits)
        if size == 0:
            return []
        path = [''] * size
        answer = []

        def search(position):
            if position == size:
                answer.append(''.join(path))
                return
            for letter in DIGIT_LETTERS[int(digits[position])]:
                path[position] = letter
                search(position + 1)
        search(0)
        return answer
```

**复杂度：** 时间 \(O(n4^n)\)，辅助空间 \(O(n)\)，输出空间最坏 \(O(n4^n)\)；\(n\) 为数字串长度。

### 组合总和（LeetCode 39）

中等 · [力扣原题](https://leetcode.cn/problems/combination-sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/combination-sum/solutions/2747858/liang-chong-fang-fa-xuan-huo-bu-xuan-mei-mhf9/)

#### 题面

给定互不相同的正整数数组 `candidates` 和正整数 `target`，找出所有能使所选数字之和等于 `target` 的组合，返回这些组合。

每个候选数字可以使用任意多次。只要每个数字使用的次数相同，就算同一种组合，不能因排列顺序不同重复输出。不同组合的输出顺序不限。 题目保证符合条件的不同组合少于 150 个。

**数据范围与约定**

- `1 <= candidates.length <= 30`
- `2 <= candidates[i] <= 40`
- `candidates` 的所有元素 互不相同
- `1 <= target <= 40`

**示例**

`candidates=[2,3,5]`、`target=7`，返回 `[[2,2,3],[2,5]]`；`[5,2]` 与 `[2,5]` 是同一个组合。

#### 解法：先判断能否凑出，再构造组合

先算表 `possible[i][amount]`：只用前 `i` 个候选数，能否凑出 `amount`，每个数可重复选。构造答案时分为选当前数、不选当前数；剩余金额在表中不可行，就立即停止这一分支。

选当前数后仍保留当前下标，允许继续使用它；不选则移到下一个候选。固定顺序保证同一组合不会因排列不同而重复出现。

```python
class Solution:

    def combinationSum(self, candidates, target):
        n = len(candidates)
        possible = [[False] * (target + 1) for _ in range(n + 1)]
        possible[0][0] = True
        for i, coin in enumerate(candidates):
            for amount in range(target + 1):
                possible[i + 1][amount] = possible[i][amount] or (amount >= coin and possible[i + 1][amount - coin])
        answer = []
        path = []

        def search(i, remaining):
            if remaining == 0:
                answer.append(path.copy())
                return
            if i < 0 or not possible[i + 1][remaining]:
                return
            search(i - 1, remaining)
            coin = candidates[i]
            if remaining >= coin:
                path.append(coin)
                search(i, remaining - coin)
                path.pop()
        search(n - 1, target)
        return answer
```

**复杂度：** 预处理 \(O(nT)\)，搜索及复制答案 \(O(V+P)\)；辅助空间 \(O(nT)\)。\(n\) 为候选数，\(T\) 为目标，\(V\) 为搜索节点数，\(P\) 为答案中的元素总数。

#### 补充：未排序的选或不选

不选当前候选数时进入下一个下标；选它时减少剩余目标，但留在当前下标以允许重复使用。剩余目标为零时复制路径。候选用完或剩余目标变负时停止。

```python
class Solution:
    def combinationSum(self, candidates, target):
        # 保留输入顺序
        answer, path = [], []
        def search(index, remaining):
            if remaining == 0:
                answer.append(path.copy())
                return
            if index == len(candidates) or remaining < 0:
                return
            search(index + 1, remaining)
            path.append(candidates[index])
            search(index, remaining - candidates[index])
            path.pop()
        search(0, target)
        return answer
```

**复杂度：** 时间 \(O(V+P)\)，辅助空间 \(O(n+D)\)。n 为候选数，V 为搜索节点数，P 为答案中的元素总数，D 为最长组合长度；最坏搜索为指数级。

**注意：** 没有排序剪枝，可能尝试许多无解分支。

#### 补充：排序后选或不选

不选当前候选数时进入下一个下标；选它时减少剩余目标，但留在当前下标以允许重复使用。剩余目标为零时复制路径。排序后若当前数已大于剩余目标，后面的数也不可能使用，立即停止。

```python
class Solution:
    def combinationSum(self, candidates, target):
        candidates.sort()
        answer, path = [], []
        def search(index, remaining):
            if remaining == 0:
                answer.append(path.copy())
                return
            if index == len(candidates) or remaining < candidates[index]:
                return
            search(index + 1, remaining)
            path.append(candidates[index])
            search(index, remaining - candidates[index])
            path.pop()
        search(0, target)
        return answer
```

**复杂度：** 时间 \(O(n\log n+V+P)\)，辅助空间 \(O(n+D)\)；符号同上一方法，最坏搜索仍为指数级。

**注意：** 会原地排序输入；排序使“不可能再凑出”的分支能提前停止。

#### 补充：枚举下一次选择哪种数

直接枚举 `path` 的下一个值，只从 `start` 及之后选，避免生成顺序不同的重复组合。选中 `pos` 后递归仍从 `pos` 开始，允许重复；排序后遇到超过剩余目标的值就结束本层循环。

```python
class Solution:
    def combinationSum(self, candidates, target):
        candidates.sort()
        answer, path = [], []
        def choose(start, remaining):
            if remaining == 0:
                answer.append(path.copy())
                return
            for pos in range(start, len(candidates)):
                value = candidates[pos]
                if value > remaining:
                    break
                path.append(value)
                choose(pos, remaining - value)
                path.pop()
        choose(0, target)
        return answer
```

**复杂度：** 时间 \(O(n\log n+V+P)\)，辅助空间 \(O(n+D)\)；符号同上，最坏搜索仍为指数级。

**注意：** 修改 `candidates` 的顺序。

### 括号生成（LeetCode 22）

中等 · [力扣原题](https://leetcode.cn/problems/generate-parentheses/) · [灵茶山艾府题解](https://leetcode.cn/problems/generate-parentheses/solutions/2071015/hui-su-bu-hui-xie-tao-lu-zai-ci-pythonja-wcdw/)

#### 题面

给定整数 `n`，生成所有由 `n` 个左括号和 `n` 个右括号组成、并且能够正确匹配的字符串。

合法匹配要求每个右括号都有它前面的左括号与之配对，且嵌套顺序正确。例如 `(())` 和 `()()` 合法，`())(` 不合法。答案顺序不限。

**数据范围与约定**

- `1 <= n <= 8`

**示例**

`n=2` 时返回 `["(())","()()"]`，两种方式都恰好使用两对括号。

#### 解法：保证每个前缀都能正确配对

逐位填写长度为 `2*n` 的字符列表。左括号还没用满时可以放左括号；已放右括号少于左括号时，才可以放右括号。这样任何前缀都不会出现无法配对的右括号，填满时就是一个合法答案。

```python
class Solution:

    def generateParenthesis(self, n):
        path = [''] * (2 * n)
        answer = []

        def search(left_count, right_count):
            if right_count == n:
                answer.append(''.join(path))
                return
            position = left_count + right_count
            if left_count < n:
                path[position] = '('
                search(left_count + 1, right_count)
            if right_count < left_count:
                path[position] = ')'
                search(left_count, right_count + 1)
        search(0, 0)
        return answer
```

**复杂度：** 时间和输出空间 \(O(nC_n)\)，辅助空间 \(O(n)\)；\(C_n=\binom{2n}{n}/(n+1)\) 为合法方案数。

#### 补充：枚举下一个左括号的位置

`openings` 只记录左括号下标，`balance` 是尚未配对的左括号数。下一个左括号之前，最多只能放 `balance` 个右括号。枚举放几个右括号，再记录左括号位置；左括号放满后，其他位置都填右括号。

```python
class Solution:
    def generateParenthesis(self, n):
        answer, openings = [], []
        def place(position, balance):
            if len(openings) == n:
                chars = [')'] * (2 * n)
                for pos in openings:
                    chars[pos] = '('
                answer.append(''.join(chars))
                return
            for closing_count in range(balance + 1):
                openings.append(position + closing_count)
                place(position + closing_count + 1, balance - closing_count + 1)
                openings.pop()
        place(0, 0)
        return answer
```

**复杂度：** 时间 \(O(nC_n)\)，辅助空间 \(O(n)\)；\(C_n\) 为合法括号串数量。

**注意：** 与逐位置选择括号相比，这里一次决定下一个左括号放在哪里。

### 单词搜索（LeetCode 79）

中等 · [力扣原题](https://leetcode.cn/problems/word-search/) · [灵茶山艾府题解](https://leetcode.cn/problems/word-search/solutions/2927294/liang-ge-you-hua-rang-dai-ma-ji-bai-jie-g3mmm/)

#### 题面

给定字符网格 `board` 和单词 `word`，判断能否在网格中找出一条路径，使沿途读到的字符依次组成 `word`。

可以从任意格子开始，每一步只能走到上、下、左、右相邻的格子，不能斜着走。在同一条路径中，每个格子最多使用一次。只需返回是否存在，不需要返回路径。

**数据范围与约定**

- `m == board.length`
- `n = board[i].length`
- `1 <= m, n <= 6`
- `1 <= word.length <= 15`
- `board` 和 `word` 仅由大小写英文字母组成

**进阶要求**

- 你可以使用搜索剪枝的技术来优化解决方案，使其在 `board` 更大的情况下可以更快解决问题？

**示例**

`[["A","B"],["C","D"]]` 可以拼出 `"ABD"`，不能拼出 `"ABA"`，后者需要重复使用左上格子。

#### 解法：从每个起点试走相邻格子

从每个格子尝试匹配单词。当前字符匹配后，临时把格子改成空字符串，防止同一路径重复使用，再尝试四个相邻方向。所有方向都失败时恢复字符；一旦匹配完整单词就立即成功返回。

```python
class Solution:

    def exist(self, board, word):
        rows, cols = (len(board), len(board[0]))

        def search(row, col, position):
            if board[row][col] != word[position]:
                return False
            if position == len(word) - 1:
                return True
            board[row][col] = ''
            for next_row, next_col in ((row, col - 1), (row, col + 1), (row - 1, col), (row + 1, col)):
                if 0 <= next_row < rows and 0 <= next_col < cols and search(next_row, next_col, position + 1):
                    return True
            board[row][col] = word[position]
            return False
        return any((search(row, col, 0) for row in range(rows) for col in range(cols)))
```

**复杂度：** 时间上界 \(O(mn3^L)\)，递归栈 \(O(L)\)；\(m,n\) 为网格行列数，\(L\) 为单词长度。

**注意：** 成功返回时不恢复成功路径上的标记，会修改输入棋盘。

#### 补充：先检查数量，再从较少见的一端搜索

棋盘字符数量不足就直接失败。末字符比首字符少见时反转 `word`，从较少的起点开始。之后逐格递归匹配，临时清空已访问位置；失败时恢复，成功时直接返回。

```python
from collections import Counter

class Solution:
    def exist(self, board, word):
        frequency = Counter(char for row in board for char in row)
        if not frequency >= Counter(word):
            return False
        if frequency[word[-1]] < frequency[word[0]]:
            word = word[::-1]
        rows, columns = len(board), len(board[0])
        def match(row, column, pos):
            if board[row][column] != word[pos]:
                return False
            if pos + 1 == len(word):
                return True
            board[row][column] = ''
            for nr, nc in ((row, column - 1), (row, column + 1), (row - 1, column), (row + 1, column)):
                if 0 <= nr < rows and 0 <= nc < columns and match(nr, nc, pos + 1):
                    return True
            board[row][column] = word[pos]
            return False
        return any(match(row, column, 0) for row in range(rows) for column in range(columns))
```

**复杂度：** 时间上界 \(O(mn3^L+mn+L)\)，空间 \(O(L+\Sigma)\)；L 为单词长度，Σ 为字符种数。

**注意：** 成功后仍不恢复路径标记。两个预检查可减少尝试次数，但最坏仍为指数级。

### 分割回文串（LeetCode 131）

中等 · [力扣原题](https://leetcode.cn/problems/palindrome-partitioning/) · [灵茶山艾府题解](https://leetcode.cn/problems/palindrome-partitioning/solutions/2059414/hui-su-bu-hui-xie-tao-lu-zai-ci-pythonja-fues/)

#### 题面

给定字符串 `s`，把它切分成若干连续的非空片段，要求每个片段正着读和反着读都相同，也就是回文串。返回所有符合条件的切分方案。

每种方案都必须完整覆盖原字符串，不能删除、跳过或重新排列字符。结果中的每个子列表是一种切分方案，里面按原顺序保存各片段。

**数据范围与约定**

- `1 <= s.length <= 16`
- `s` 仅由小写英文字母组成

**示例**

`s="aba"` 的答案是 `[["a","b","a"],["aba"]]`，每段都是回文。

#### 解法：枚举下一段在哪里结束

从尚未切分的位置开始，逐个尝试当前段的终点。只有这段正反读相同时，才把它加入路径，继续切分后面的字符串；返回后移除这段。到达串尾时复制当前路径，得到一个完整方案。

```python
class Solution:

    def partition(self, s):
        answer = []
        path = []

        def search(start):
            if start == len(s):
                answer.append(path.copy())
                return
            for end in range(start + 1, len(s) + 1):
                piece = s[start:end]
                if piece != piece[::-1]:
                    continue
                path.append(piece)
                search(end)
                path.pop()
        search(0)
        return answer
```

**复杂度：** 时间 \(O(n2^n)\)，辅助空间 \(O(n)\)，输出空间最坏 \(O(n2^n)\)；\(n\) 为字符串长度。

#### 补充：决定每个字符后面是否切开

`index` 是当前结尾，`start` 是尚未切下的一段起点。可以延长当前段，也可以在此切开；切出的子串是回文时才继续。最后一位后必须切开，确保包含全部字符。

```python
class Solution:
    def partition(self, s):
        answer, path = [], []
        def split(index, start):
            if index == len(s):
                answer.append(path.copy())
                return
            if index + 1 < len(s):
                split(index + 1, start)
            piece = s[start:index + 1]
            if piece == piece[::-1]:
                path.append(piece)
                split(index + 1, index + 1)
                path.pop()
        split(0, 0)
        return answer
```

**复杂度：** 时间 \(O(n2^n)\)，辅助空间 \(O(n)\)，不计答案。

### N 皇后（LeetCode 51）

困难 · [力扣原题](https://leetcode.cn/problems/n-queens/) · [灵茶山艾府题解](https://leetcode.cn/problems/n-queens/solutions/2079586/hui-su-tao-lu-miao-sha-nhuang-hou-shi-pi-mljv/)

#### 题面

给定正整数 `n`，在一个 `n` 行、`n` 列的棋盘上放置 `n` 个皇后，使任何两个皇后都不能相互攻击。返回所有不同的合法摆法。

皇后会攻击同一行、同一列以及两种斜线上的其他皇后。每种答案用 `n` 个字符串表示棋盘，`'Q'` 表示皇后、`'.'` 表示空格；不同方案的输出顺序不限。

**数据范围与约定**

- `1 <= n <= 9`

**示例**

`n=4` 的一种答案为 `[".Q..","...Q","Q...","..Q."]`，各行皇后列下标为 `[1,3,0,2]`。

#### 解法：每行放一个皇后，记录被占用的列和斜线

逐行尝试列位置，用三个布尔数组记录已占用的列和两种斜线。同一条斜线上的格子，行列之和相同，或行列之差相同。所选列和斜线都未占用时才放皇后；递归返回后撤销占用。填满所有行，再生成棋盘。

```python
class Solution:

    def solveNQueens(self, n):
        chosen = [0] * n
        columns = [False] * n
        rising = [False] * (2 * n - 1)
        falling = [False] * (2 * n - 1)
        answer = []

        def search(row):
            if row == n:
                answer.append(['.' * col + 'Q' + '.' * (n - col - 1) for col in chosen])
                return
            for col in range(n):
                diagonal_sum = row + col
                diagonal_difference = row - col + n - 1
                if not columns[col] and (not rising[diagonal_sum]) and (not falling[diagonal_difference]):
                    chosen[row] = col
                    columns[col] = rising[diagonal_sum] = falling[diagonal_difference] = True
                    search(row + 1)
                    columns[col] = rising[diagonal_sum] = falling[diagonal_difference] = False
        search(0)
        return answer
```

**复杂度：** 时间上界 \(O(n^2n!)\)，辅助空间 \(O(n)\)；\(n\) 为棋盘边长，若有 \(k\) 个答案，输出空间为 \(O(kn^2)\)。

**注意：** 代码给行列之差加 `n-1`，使它成为非负数组下标。


## 二分查找

### 搜索插入位置（LeetCode 35）

简单 · [力扣原题](https://leetcode.cn/problems/search-insert-position/) · [灵茶山艾府题解](https://leetcode.cn/problems/search-insert-position/solutions/2023391/er-fen-cha-zhao-zong-shi-xie-bu-dui-yi-g-nq23/)

#### 题面

给定已按从小到大排列、没有重复元素的数组 `nums` 和整数 `target`。如果 `target` 在数组中，返回它的下标；否则返回把它插入后仍能保持有序的位置。

插入位置从 0 开始计数，也可能等于数组长度，表示插在末尾。要求时间复杂度为 \(O(\log n)\)。

**数据范围与约定**

- `1 <= nums.length <= 10^4`
- `-10^4 <= nums[i] <= 10^4`
- `nums` 为 无重复元素 的 升序 排列数组
- `-10^4 <= target <= 10^4`

**示例**

`nums=[1,4,7]`，`target=5` 返回 `2`；`target=9` 返回 `3`，表示插在末尾。

#### 解法：二分找第一个不小于目标的数

在左闭右开的范围内二分。中点值小于目标时，插入位置必在右边；否则中点可能就是答案，保留它并缩小右边界。范围缩为空时，边界就是插入位置；若所有数都更小，结果自然等于数组长度。

```python
class Solution:

    def searchInsert(self, nums, target):
        left, right = (0, len(nums))
        while left < right:
            middle = (left + right) // 2
            if nums[middle] < target:
                left = middle + 1
            else:
                right = middle
        return left
```

**复杂度：** 时间 \(O(\log n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**写法补充：** 原文还给出 `bisect_left` 标准库写法，寻找的插入边界相同。

### 搜索二维矩阵（LeetCode 74）

中等 · [力扣原题](https://leetcode.cn/problems/search-a-2d-matrix/) · [灵茶山艾府题解](https://leetcode.cn/problems/search-a-2d-matrix/solutions/2783931/liang-chong-fang-fa-er-fen-cha-zhao-pai-39d74/)

#### 题面

给定矩阵 `matrix` 和整数 `target`，判断 `target` 是否出现在矩阵中，返回布尔值。矩阵每行已按从小到大排列，而且下一行的第一个数严格大于上一行的最后一个数。

因此按行把所有元素接起来后，整体也是有序的。要求搜索时间为 \(O(\log(mn))\)，其中 \(m,n\) 是行数和列数。

**数据范围与约定**

- `m == matrix.length`
- `n == matrix[i].length`
- `1 <= m, n <= 100`
- `-10^4 <= matrix[i][j], target <= 10^4`

**示例**

`matrix=[[1,3,5],[7,9,11]]`、`target=9`，返回 `True`；`9` 位于第二行第二列。

#### 解法：把矩阵当作有序的一维数组

按行连接后，整个矩阵有序，可以直接二分一维下标，不必真的展开。若列数为 `cols`，下标 `middle` 对应 `matrix[middle//cols][middle%cols]`。中点值等于目标就成功，小于目标向右找，大于目标向左找；范围为空则失败。

```python
class Solution:

    def searchMatrix(self, matrix, target):
        rows, cols = (len(matrix), len(matrix[0]))
        left, right = (-1, rows * cols)
        while left + 1 < right:
            middle = (left + right) // 2
            value = matrix[middle // cols][middle % cols]
            if value == target:
                return True
            if value < target:
                left = middle
            else:
                right = middle
        return False
```

**复杂度：** 时间 \(O(\log(mn))\)，额外空间 \(O(1)\)；\(m,n\) 为矩阵行列数。

**写法补充：** 原文另有标准库二分写法，同样把二维位置映射为一维。

### 在排序数组中查找元素的第一个和最后一个位置（LeetCode 34）

中等 · [力扣原题](https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/) · [灵茶山艾府题解](https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/solutions/1980196/er-fen-cha-zhao-zong-shi-xie-bu-dui-yi-g-t9l9/)

#### 题面

给定按非递减顺序排列的数组 `nums` 和整数 `target`，返回 `target` 第一次和最后一次出现的下标，形式为 `[first,last]`。

数组可能包含重复值。不存在目标时返回 `[-1,-1]`；只有一次时两个下标相同。要求时间复杂度为 \(O(\log n)\)。

**数据范围与约定**

- `0 <= nums.length <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `nums` 是一个非递减数组
- `-10^9 <= target <= 10^9`

**示例**

`nums=[1,2,2,2,4]`、`target=2`，返回 `[1,3]`；查找 `3` 则返回 `[-1,-1]`。

#### 解法：两次二分确定重复段边界

第一次找首个不小于 `target` 的位置；若这里不是目标，直接返回 `[-1,-1]`。第二次找首个严格大于 `target` 的位置，它前一个位置就是最后一次出现。相同值连续排列，因此这两个边界能夹住整段目标值。

```python
class Solution:

    def searchRange(self, nums, target):

        def boundary(strict):
            left, right = (0, len(nums))
            while left < right:
                middle = (left + right) // 2
                if nums[middle] < target or (strict and nums[middle] == target):
                    left = middle + 1
                else:
                    right = middle
            return left
        first = boundary(False)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, boundary(True) - 1]
```

**复杂度：** 时间 \(O(\log n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**写法补充：** 原文用不同的区间开闭约定、严格比较或目标加一来寻找同一对边界。

### 搜索旋转排序数组（LeetCode 33）

中等 · [力扣原题](https://leetcode.cn/problems/search-in-rotated-sorted-array/) · [灵茶山艾府题解](https://leetcode.cn/problems/search-in-rotated-sorted-array/solutions/1987503/by-endlesscheng-auuh/)

#### 题面

给定数组 `nums` 和整数 `target`。`nums` 原本严格递增，之后可能在某个位置被切成两段，并把后段整体移到前面，例如 `[1,3,5,7]` 变成 `[5,7,1,3]`。查找 `target` 并返回下标。

数组中没有重复值。如果目标不存在，返回 `-1`。要求时间复杂度为 \(O(\log n)\)。

**数据范围与约定**

- `1 <= nums.length <= 5000`
- `-10^4 <= nums[i] <= 10^4`
- `nums` 中的每个值都 独一无二
- 题目数据保证 `nums` 在预先未知的某个下标上进行了旋转
- `-10^4 <= target <= 10^4`

**示例**

`nums=[6,8,1,3,5]`、`target=3`，返回下标 `3`；目标不存在则返回 `-1`。

#### 解法：判断中点与目标是否位于同一有序段

用数组末值区分较大的前段和较小的后段。若中点与目标在同一段，直接按数值大小二分；若不在同一段，前段一定在后段左边，按这个位置关系缩小范围。数组未旋转时，所有元素都属于同一段，仍可正常搜索。

```python
class Solution:

    def search(self, nums, target):
        left, right = (0, len(nums) - 1)
        last = nums[-1]
        while left <= right:
            middle = (left + right) // 2
            value = nums[middle]
            if value == target:
                return middle
            if (value > last) == (target > last):
                move_right = value < target
            else:
                move_right = value > last
            if move_right:
                left = middle + 1
            else:
                right = middle - 1
        return -1
```

**复杂度：** 时间 \(O(\log n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

#### 补充：先找旋转点，再搜索所在的有序段

第一次二分找到最小值下标。目标大于末元素时只可能在前段，否则只可能在后段；第二次二分在相应区间找第一个不小于目标的位置，最后检查相等。

```python
class Solution:
    def search(self, nums, target):
        low, high = -1, len(nums) - 1
        while high - low > 1:
            middle = (low + high) // 2
            if nums[middle] < nums[-1]:
                high = middle
            else:
                low = middle
        pivot = high
        if target > nums[-1]:
            low, high = -1, pivot
        else:
            low, high = pivot - 1, len(nums)
        while high - low > 1:
            middle = (low + high) // 2
            if nums[middle] >= target:
                high = middle
            else:
                low = middle
        return high if nums[high] == target else -1
```

**复杂度：** 时间 \(O(\log n)\)，额外空间 \(O(1)\)。

**注意：** 两次对数时间相加仍为对数时间。

**写法补充：** 一次二分可写成显式分支、合并判断条件或标准库调用；先找旋转点的方法已另列。

### 寻找旋转排序数组中的最小值（LeetCode 153）

中等 · [力扣原题](https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/) · [灵茶山艾府题解](https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/solutions/1987499/by-endlesscheng-owgd/)

#### 题面

给定没有重复元素的数组 `nums`。它原本按从小到大排列，之后经过了轮转：一部分末尾元素按原顺序移动到开头。返回数组中的最小值。

轮转可能恰好完成一整圈，因此输入仍可能是普通的递增数组。要求时间复杂度为 \(O(\log n)\)。

**数据范围与约定**

- `n == nums.length`
- `1 <= n <= 5000`
- `-5000 <= nums[i] <= 5000`
- `nums` 中的所有整数 互不相同
- `nums` 原来是一个升序排序的数组，并进行了 1 至 n 次旋转

**示例**

`[4,7,9,1,2]` 返回 `1`；未旋转的 `[1,2,4]` 也返回 `1`。

#### 解法：固定与数组末值比较

中点大于末值，说明它位于较大的前段，最小值一定在右边；中点小于末值，最小值在中点或左边。按此缩小范围即可，未旋转的数组也适用。代码不把最后一个下标选作中点，因此无需处理相等分支。

```python
class Solution:

    def findMin(self, nums):
        left, right = (-1, len(nums) - 1)
        last = nums[-1]
        while left + 1 < right:
            middle = (left + right) // 2
            if nums[middle] < last:
                right = middle
            else:
                left = middle
        return nums[right]
```

**复杂度：** 时间 \(O(\log n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**写法补充：** 原文也讨论与首值比较：从下标一开始找较小段；若没找到，说明未旋转，返回首值。另有与末值比较的标准库版本。

### 寻找两个正序数组的中位数（LeetCode 4）

困难 · [力扣原题](https://leetcode.cn/problems/median-of-two-sorted-arrays/) · [灵茶山艾府题解](https://leetcode.cn/problems/median-of-two-sorted-arrays/solutions/2950686/tu-jie-xun-xu-jian-jin-cong-shuang-zhi-z-p2gd/)

#### 题面

给定两个分别按从小到大排列的数组 `nums1` 和 `nums2`，返回把它们的全部元素放在一起并按大小排列后的中位数。

总元素个数为奇数时，中位数是中间一个数；为偶数时，是中间两个数的平均值。允许一个数组为空，但两个不能同时为空；要求时间复杂度为 \(O(\log(m+n))\)。

**数据范围与约定**

- `nums1.length == m`
- `nums2.length == n`
- `0 <= m <= 1000`
- `0 <= n <= 1000`
- `1 <= m + n <= 2000`
- `-10^6 <= nums1[i], nums2[i] <= 10^6`

**示例**

`nums1=[1,4]`、`nums2=[2,3,8]`，合并后的顺序为 `[1,2,3,4,8]`，中位数是 `3`。

#### 解法：二分两个数组的分割位置

先让 `a` 是较短数组。左右分组后，左组固定有 `half` 个元素，比右组多一个或与它一样多。`a` 的左组最后下标为 `cut`，即取了 `cut+1` 项，所以 `b` 的对应下标是 `half-cut-2`。

二分找最后一个满足“`a` 左组末值不大于 `b` 右组首值”的位置。此时反方向也必须满足：否则 `b` 左组末值仍大于 `a` 的下一项，还能从 `a` 多取一项，与“最后一个”矛盾。两侧大小关系都正确后，就可从边界读取中位数。

```python
class Solution:

    def findMedianSortedArrays(self, nums1, nums2):
        a, b = (nums1, nums2)
        if len(a) > len(b):
            a, b = (b, a)
        m, n = (len(a), len(b))
        left, right = (-1, m)
        half = (m + n + 1) // 2
        while left + 1 < right:
            cut = (left + right) // 2
            other = half - cut - 2
            if a[cut] <= b[other + 1]:
                left = cut
            else:
                right = cut
        cut = left
        other = half - cut - 2
        a_left = a[cut] if cut >= 0 else float('-inf')
        b_left = b[other] if other >= 0 else float('-inf')
        a_right = a[cut + 1] if cut + 1 < m else float('inf')
        b_right = b[other + 1] if other + 1 < n else float('inf')
        lower_middle = max(a_left, b_left)
        if (m + n) % 2:
            return lower_middle
        return (lower_middle + min(a_right, b_right)) / 2
```

**复杂度：** 时间 \(O(\log(\min(m,n)+1))\)，额外空间 \(O(1)\)；\(m,n\) 为两数组长度。

**注意：** 空的左、右半边按负无穷、正无穷处理；只在比较时使用，不复制数组。

#### 补充：连接后排序取中位数

连接两数组后排序。奇数长度取中间一项，偶数长度取中间两项平均值。

```python
class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        values = sorted(nums1 + nums2)
        middle = (len(values) - 1) // 2
        return values[middle] if len(values) % 2 else (values[middle] + values[middle + 1]) / 2
```

**复杂度：** 按通用排序上界，时间 \(O((m+n)\log(m+n))\)，空间 \(O(m+n)\)。

**注意：** 教学引入。Python 排序可利用已有序段加速，但这份实现仍不满足题目的对数时间要求。

#### 补充：双指针枚举分割位置

左组固定放总元素数的一半向上取整。`take_a`、`take_b` 是两数组各放入多少项。若 `a` 的下一项不大于 `b` 的左组末项，就让 `a` 多放一项、`b` 少放一项，直到分割两侧有序，再从边界取中位数。

```python
from math import inf

class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        short, total = len(a), len(a) + len(b)
        a, b = [-inf] + a + [inf], [-inf] + b + [inf]

        take_a, take_b = 0, (total + 1) // 2
        while a[take_a + 1] <= b[take_b]:
            take_a += 1
            take_b -= 1

        lower = max(a[take_a], b[take_b])
        upper = min(a[take_a + 1], b[take_b + 1])
        return lower if total % 2 else (lower + upper) / 2
```

**复杂度：** 时间 \(O(m+n)\)，空间 \(O(m+n)\)，包含添加哨兵时复制数组。

**注意：** 枚举的是分割位置，没有逐个合并数组。

#### 补充：实际添加哨兵的二分分割

固定左组元素总数，只二分短数组 `a` 放入多少项。若 `a` 的左组末项不大于 `b` 的右组首项，就尝试多放；否则少放。取最后一个满足的位置，再读两组边界。

```python
from math import inf

class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        a, b = nums1, nums2
        if len(a) > len(b):
            a, b = b, a
        short, total = len(a), len(a) + len(b)
        a, b = [-inf] + a + [inf], [-inf] + b + [inf]

        low, high = 0, short + 1
        while high - low > 1:
            take_a = (low + high) // 2
            take_b = (total + 1) // 2 - take_a
            if a[take_a] <= b[take_b + 1]:
                low = take_a
            else:
                high = take_a
        take_a, take_b = low, (total + 1) // 2 - low

        lower = max(a[take_a], b[take_b])
        upper = min(a[take_a + 1], b[take_b + 1])
        return lower if total % 2 else (lower + upper) / 2
```

**复杂度：** 二分部分 \(O(\log(\min(m,n)+1))\)；加哨兵要复制数组，因此总时间、空间都是 \(O(m+n)\)。

**注意：** 主解法按需处理越界值，省去复制，才达到整体对数时间。

**写法补充：** 原文另有双指针中增加一次交叉检查，以及用标准库完成二分的等价写法。


## 栈

### 有效的括号（LeetCode 20）

简单 · [力扣原题](https://leetcode.cn/problems/valid-parentheses/) · [灵茶山艾府题解](https://leetcode.cn/problems/valid-parentheses/solutions/2809539/gua-hao-xiao-xiao-le-san-chong-li-yong-z-2xb3/)

#### 题面

给定只包含 `(`、`)`、`[`、`]`、`{`、`}` 的字符串 `s`，判断里面的括号是否全部正确匹配。

每个右括号必须与前面同类型的左括号配对，且嵌套顺序要正确；不能剩下未配对的括号。例如 `([])` 合法，`([)]` 不合法。返回布尔值。

**数据范围与约定**

- `1 <= s.length <= 10^4`
- `s 仅由括号 '()[]{}' 组成`

**示例**

`"{[()]}"` 返回 `True`；`"{[(])}"` 返回 `False`，因为 `]` 前最近未配对的左括号是 `(`。

#### 解法：栈匹配最近的左括号

每个左括号都要对应一个右括号，所以奇数长度可直接判错。扫描时把左括号压栈；遇到右括号，它必须匹配栈顶的左括号，否则失败。扫描结束后栈还必须为空，确保没有遗漏的左括号。

```python
class Solution:

    def isValid(self, s):
        if len(s) % 2:
            return False
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []
        for char in s:
            if char not in pairs:
                stack.append(char)
            elif not stack or stack.pop() != pairs[char]:
                return False
        return not stack
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(n)\)；\(n\) 为字符串长度。

#### 补充：栈内保存期待的右括号

遇到左括号时压入对应右括号。遇到右括号时必须与栈顶相同，栈空或不同就失败；最后栈应为空。奇数长度提前失败。

```python
class Solution:
    def isValid(self, s):
        if len(s) % 2:
            return False
        closing = {'(': ')', '[': ']', '{': '}'}
        expected = []
        for char in s:
            if char in closing:
                expected.append(closing[char])
            elif not expected or expected.pop() != char:
                return False
        return not expected
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** 与存左括号的方法同阶，区别只是栈内信息的含义。

**写法补充：** 期待的右括号可以用字典映射，也可以用 `if/elif` 分支确定。

### 最小栈（LeetCode 155）

中等 · [力扣原题](https://leetcode.cn/problems/min-stack/) · [灵茶山艾府题解](https://leetcode.cn/problems/min-stack/solutions/2974438/ben-zhi-shi-wei-hu-qian-zhui-zui-xiao-zh-x0g8/)

#### 题面

实现 `MinStack`：它像普通栈一样保存整数，最后放进去的元素最先被取出；同时还能随时返回当前栈里的最小值。

`MinStack()` 创建空栈；`push(val)` 放入一个值；`pop()` 删除最后放入且尚未删除的值；`top()` 查看这个值但不删除；`getMin()` 返回栈中最小值。每种操作要求常数时间，读栈或弹栈时题目保证栈非空。

**数据范围与约定**

- `-2^31 <= val <= 2^31 - 1`
- `pop` 、 `top` 和 `getMin` 操作总是在 非空栈 上调用
- `push` , `pop` , `top` , and `getMin` 最多被调用 3 * 10^4 次

**示例**

依次压入 `4、2、3`，最小值为 `2`；弹出 `3` 后仍为 `2`，再弹出 `2` 后恢复为 `4`。

#### 解法：每层同时保存当前最小值

每次入栈保存两项：本次数值，以及从栈底到这一层的最小值。新最小值只需与上一层比较得到。弹出顶层后，下一层已经保存好此前的最小值，查询时直接读栈顶即可。

```python
class MinStack:

    def __init__(self):
        self.stack = []

    def push(self, val):
        minimum = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, minimum))

    def pop(self):
        self.stack.pop()

    def top(self):
        return self.stack[-1][0]

    def getMin(self):
        return self.stack[-1][1]
```

**复杂度：** 每次操作均摊 \(O(1)\)，空间 \(O(q)\)；\(q\) 为栈内元素数。

#### 补充：保存与旧最小值的差

`push` 记录 `val` 减去旧最小值的差，再更新最小值。差为负，说明这一项刷新了最小值；`pop` 时减去这个负差就恢复旧值。读取栈顶时，差为负则值就是当前最小值，差非负则把两者相加。

```python
from math import inf

class MinStack:
    def __init__(self):
        self.differences = []
        self.minimum = inf

    def push(self, val):
        self.differences.append(val - self.minimum)
        self.minimum = min(self.minimum, val)

    def pop(self):
        difference = self.differences.pop()
        if difference < 0:
            self.minimum -= difference

    def top(self):
        return self.minimum + max(0, self.differences[-1])

    def getMin(self):
        return self.minimum
```

**复杂度：** 每次操作 \(O(1)\)，空间 \(O(n)\)。

**注意：** 首项利用正无穷初始化；每层只保存一个差，栈的总空间仍为线性。

### 字符串解码（LeetCode 394）

中等 · [力扣原题](https://leetcode.cn/problems/decode-string/) · [灵茶山艾府题解](https://leetcode.cn/problems/decode-string/solutions/3744428/di-gui-yong-zhan-mo-ni-di-gui-pythonjava-kcsv/)

#### 题面

给定编码字符串 `s`，按照 `k[内容]` 的规则解码：方括号里的内容需要重复 `k` 次，普通字母保持不变。返回完整解码结果。

括号可以嵌套，应先理解内层再执行外层重复；例如 `2[a3[b]]` 表示把 `abbb` 重复两次。重复次数是正整数，可能有多位。题目保证编码合法，数字只表示重复次数。 题目还保证解码结果长度不超过 \(10^5\)。

**数据范围与约定**

- `1 <= s.length <= 30`
- `s 由小写英文字母、数字和方括号 '[]' 组成`
- `s` 保证是一个 有效 的输入。
- `s 中所有整数的取值范围为 [1, 300]`

**示例**

`"2[a3[b]]"` 解码为 `"abbbabbb"`：内部先得到 `"abbb"`，再重复两次。

#### 解法：用栈保存暂时中断的外层内容

读数字时累计重复次数。遇到左括号，把外层已解码前缀和次数压栈，开始处理新的内层；遇到右括号，内层已完成，将它重复指定次数，再接回外层前缀。普通字母直接加入当前内容。

```python
class Solution:

    def decodeString(self, s):
        stack = []
        current = ''
        repeat = 0
        for char in s:
            if char.isdigit():
                repeat = repeat * 10 + int(char)
            elif char == '[':
                stack.append((current, repeat))
                current = ''
                repeat = 0
            elif char == ']':
                prefix, count = stack.pop()
                current = prefix + current * count
            else:
                current += char
        return current
```

**复杂度：** 时间保守上界 \(O(nL)\)，含结果空间 \(O(n+L)\)；\(n\) 为输入长度，\(L\) 为输出长度，计入字符串复制。

#### 补充：切出括号内容后递归

开头是字母时，保留它并递归解码后缀；是数字时，找到对应左括号，再统计未闭合括号数，找到匹配的右括号。分别解码括号内部和后缀，再按次数重复并拼接。

```python
class Solution:
    def decodeString(self, s):
        if not s:
            return s
        if s[0].isalpha():
            return s[0] + self.decodeString(s[1:])
        opening = s.index('[')
        balance = 1
        for end in range(opening + 1, len(s)):
            if s[end] == '[':
                balance += 1
            elif s[end] == ']':
                balance -= 1
                if balance == 0:
                    inside = self.decodeString(s[opening + 1:end])
                    suffix = self.decodeString(s[end + 1:])
                    return inside * int(s[:opening]) + suffix
```

**复杂度：** 输入长 n、输出长 L；反复查找、切片及拼接的保守时间上界 \(O(n^2+nL)\)，空间上界 \(O(n^2+L)\)。

**注意：** 反复寻找右括号和切片会有额外开销，后面的共享下标版本可以省去这些工作。

#### 补充：共享下标递归，累加字符串

`position` 指向下一个未读字符；数字逐位组成次数，左括号开启递归，右括号结束本层。使用次数后归零，避免影响相邻片段。本层直接累加字符串，拼接可能反复复制已有前缀。

```python
class Solution:
    def decodeString(self, s):
        position = 0
        def read():
            nonlocal position
            parts = ''
            repeats = 0
            while position < len(s):
                char = s[position]
                position += 1
                if char.isalpha():
                    parts += char
                elif char.isdigit():
                    repeats = 10 * repeats + int(char)
                elif char == '[':
                    parts += read() * repeats
                    repeats = 0
                else:
                    break
            return parts
        return read()
```

**复杂度：** 考虑字符串复制，保守时间上界 \(O(n+nL)\)，含输出空间 \(O(n+L)\)。n 为输入长，L 为输出长。

**注意：** 字符串累加可能反复复制已有前缀。

#### 补充：共享下标递归，最后 join

`position` 指向下一个未读字符；数字逐位组成次数，左括号开启递归，右括号结束本层。使用次数后归零，避免影响相邻片段。本层先保存片段，结束时一次 `join`，减少反复复制前缀。

```python
class Solution:
    def decodeString(self, s):
        position = 0
        def read():
            nonlocal position
            parts = []
            repeats = 0
            while position < len(s):
                char = s[position]
                position += 1
                if char.isalpha():
                    parts.append(char)
                elif char.isdigit():
                    repeats = 10 * repeats + int(char)
                elif char == '[':
                    parts.append(read() * repeats)
                    repeats = 0
                else:
                    break
            return ''.join(parts)
        return read()
```

**复杂度：** 时间 \(O(n+B)\)，含结果空间 \(O(n+L)\)；n 为输入长度，L 为输出长度，B 为各层构造字符串的总长度。

**注意：** 先存片段再 `join`，减少重复复制前缀；嵌套重复仍会构造中间字符串。

### 每日温度（LeetCode 739）

中等 · [力扣原题](https://leetcode.cn/problems/daily-temperatures/) · [灵茶山艾府题解](https://leetcode.cn/problems/daily-temperatures/solutions/2470179/shi-pin-jiang-qing-chu-wei-shi-yao-yao-y-k0ks/)

#### 题面

给定数组 `temperatures`，其中每项是对应那一天的温度。对每一天，从它之后的日期中找到第一个温度严格更高的日子，返回还要等待多少天。

结果与输入等长。如果后面再也没有更高温度，该天的结果为 0。温度相同不算更高，今天本身也不算等待后的日期。

**数据范围与约定**

- `1 <= temperatures.length <= 10^5`
- `30 <= temperatures[i] <= 100`

**示例**

`[60,59,61]` 返回 `[2,1,0]`：前两天分别等两天、一天升温，最后一天无后续日期。

#### 解法：从右向左维护更暖日期的候选

栈存右侧日期的下标。处理今天时，弹出温度不高于今天的候选：它们更远、也不更暖，以后可以由今天替代。剩下的栈顶就是最近的更暖日期，用下标差得到等待天数；栈空则为零。

```python
class Solution:

    def dailyTemperatures(self, temperatures):
        answer = [0] * len(temperatures)
        stack = []
        for i in range(len(temperatures) - 1, -1, -1):
            while stack and temperatures[stack[-1]] <= temperatures[i]:
                stack.pop()
            if stack:
                answer[i] = stack[-1] - i
            stack.append(i)
        return answer
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(\min(n,U))\)，输出另计；\(n\) 为天数，\(U\) 为温度取值范围大小。

#### 补充：从左向右处理等待升温的日期

栈保存还没有答案的日期，温度从底到顶不升。今天温度更高时，弹出比今天冷的日期，今天就是它们第一次遇到的更暖日，日期差就是答案。

```python
class Solution:
    def dailyTemperatures(self, temperatures):
        waits = [0] * len(temperatures)
        unresolved = []
        for today, value in enumerate(temperatures):
            while unresolved and temperatures[unresolved[-1]] < value:
                earlier = unresolved.pop()
                waits[earlier] = today - earlier
            unresolved.append(today)
        return waits
```

**复杂度：** 时间 \(O(n)\)，除答案外空间 \(O(n)\)。

**注意：** 同温不算升温；每个日期至多入栈、出栈一次。

### 柱状图中最大的矩形（LeetCode 84）

困难 · [力扣原题](https://leetcode.cn/problems/largest-rectangle-in-histogram/) · [灵茶山艾府题解](https://leetcode.cn/problems/largest-rectangle-in-histogram/solutions/2695467/dan-diao-zhan-fu-ti-dan-pythonjavacgojsr-89s7/)

#### 题面

给定非负整数数组 `heights`，每项表示一根宽度为一的柱子高度，所有柱子从左到右紧挨着排列。求这个柱状图内部能够放下的最大矩形面积。

矩形覆盖一段连续的横向范围，不能超出该范围内任何柱子的高度。可以只覆盖一根柱子，也可以覆盖多根；返回面积数值。

**数据范围与约定**

- `1 <= heights.length <=10^5`
- `0 <= heights[i] <= 10^4`

**示例**

`[2,4,4,1]` 返回 `8`，取中间两根高 `4` 的柱子，宽度为 `2`。

#### 解法：遇到更矮柱子时计算矩形

栈保存高度递增的柱子下标。遇到更矮或等高的柱子，就弹出旧柱子并计算以它为高的矩形：弹出后的栈顶给出左边界，当前下标给出右边界，宽度是两者之差减一。

等高时让较后的柱子继续代表这一高度，仍可得到更宽的矩形。末尾追加高度 `-1`，确保剩余柱子也会被弹出处理。

```python
class Solution:

    def largestRectangleArea(self, heights):
        heights.append(-1)
        stack = [-1]
        answer = 0
        for right, current in enumerate(heights):
            while len(stack) > 1 and heights[stack[-1]] >= current:
                position = stack.pop()
                left = stack[-1]
                answer = max(answer, heights[position] * (right - left - 1))
            stack.append(right)
        return answer
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(n)\)；\(n\) 为柱子个数。每个下标最多入栈出栈各一次。

**注意：** 会在输入数组末尾追加 `-1`。

#### 补充：三次遍历：左右边界分别求

以某柱高度作矩形高，左右能延伸到第一根更矮柱子之前。左右各扫一次，用栈求严格更矮边界；最后计算高度乘边界之间的宽度。

```python
class Solution:
    def largestRectangleArea(self, heights):
        size = len(heights)
        left, right = [-1] * size, [size] * size
        stack = []
        for pos in range(size):
            while stack and heights[stack[-1]] >= heights[pos]:
                stack.pop()
            if stack:
                left[pos] = stack[-1]
            stack.append(pos)
        stack.clear()
        for pos in range(size - 1, -1, -1):
            while stack and heights[stack[-1]] >= heights[pos]:
                stack.pop()
            if stack:
                right[pos] = stack[-1]
            stack.append(pos)
        return max(heights[pos] * (right[pos] - left[pos] - 1) for pos in range(size))
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** 不修改 `heights`。

#### 补充：两次遍历：同时记录左右边界

遇到更矮或等高柱子时，记录被弹出位置的右边界；剩余栈顶是当前柱的严格更矮左边界。最后统一计算面积。等高柱子由较右的一根接管更宽范围，因此不漏最大值。

```python
class Solution:
    def largestRectangleArea(self, heights):
        size = len(heights)
        left, right = [-1] * size, [size] * size
        stack = []
        for pos, value in enumerate(heights):
            while stack and heights[stack[-1]] >= value:
                right[stack.pop()] = pos
            if stack:
                left[pos] = stack[-1]
            stack.append(pos)
        return max(heights[pos] * (right[pos] - left[pos] - 1) for pos in range(size))
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** 右边界允许等高，左边界严格更矮；与三遍版边界含义不同。不修改输入。


## 堆

### 数组中的第K个最大元素（LeetCode 215）

中等 · [力扣原题](https://leetcode.cn/problems/kth-largest-element-in-an-array/) · [灵茶山艾府题解](https://leetcode.cn/problems/kth-largest-element-in-an-array/solutions/3799769/on-kuai-su-xuan-ze-suan-fa-pythonjavaccg-lh7c/)

#### 题面

给定整数数组 `nums` 和整数 `k`，返回数组中的第 `k` 大元素。也就是把数组按从大到小排列后，取第 `k` 个位置的值。

重复值照常占据排名，例如 `[5,5,3]` 的第二大仍是 5。`k` 从 1 开始且一定有效；题目要求线性时间的算法。

**数据范围与约定**

- `1 <= k <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

**示例**

`nums=[7,2,5,5,1]`、`k=2`，返回 `5`；两个 `5` 分别占第二、第三名。

#### 解法：随机选择基准，只处理答案所在的一侧

第 `k` 大对应升序下标 `len(nums)-k`。随机选一个基准值，用左右指针把不大于它的值放左边、不小于它的值放右边，确定基准的位置。目标下标在哪一侧，就只继续处理那一侧，无需排好整个数组。遇到等值元素也推进指针，避免卡住。

```python
from random import randrange

class Solution:

    def findKthLargest(self, nums, k):
        target = len(nums) - k
        low, high = (0, len(nums) - 1)
        while True:
            selected = randrange(low, high + 1)
            nums[low], nums[selected] = (nums[selected], nums[low])
            pivot = nums[low]
            i, j = (low + 1, high)
            while True:
                while i <= j and nums[i] < pivot:
                    i += 1
                while i <= j and nums[j] > pivot:
                    j -= 1
                if i >= j:
                    break
                nums[i], nums[j] = (nums[j], nums[i])
                i += 1
                j -= 1
            nums[low], nums[j] = (nums[j], nums[low])
            if j == target:
                return nums[j]
            if j < target:
                low = j + 1
            else:
                high = j - 1
```

**复杂度：** 期望时间 \(O(n)\)，最坏 \(O(n^2)\)；额外空间 \(O(1)\)。\(n\) 为数组长度，所选实现不递归。

**注意：** 会修改输入数组；随机化保证期望线性时间，最坏仍可能平方级。

### 前 K 个高频元素（LeetCode 347）

中等 · [力扣原题](https://leetcode.cn/problems/top-k-frequent-elements/) · [灵茶山艾府题解](https://leetcode.cn/problems/top-k-frequent-elements/solutions/3655287/tong-pai-xu-on-xian-xing-zuo-fa-pythonja-oqq2/)

#### 题面

给定整数数组 `nums` 和整数 `k`，统计各个不同数值出现的次数，返回出现次数最多的 `k` 个数值。

返回数值而不是次数，结果顺序不限。题目保证答案集合唯一。

**数据范围与约定**

- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `k 的取值范围是 [1, 数组中不相同的元素的个数]`
- 题目数据保证答案唯一，换句话说，数组中前 `k` 个高频元素的集合是唯一的

**进阶要求**

- 你所设计算法的时间复杂度 必须 优于 \(O(n \log n)\) ，其中 n 是数组大小。

**示例**

`nums=[4,4,1,1,1,8]`、`k=2`，返回 `[1,4]`，它们分别出现三次、两次。

#### 解法：按出现次数分桶

先统计每个数出现几次，再用次数作下标，把同频次的数放进同一个桶。从高频桶往低频桶收集，得到前 `k` 个数。题目保证答案集合唯一，因此不会需要从答案边界上的同频桶里只选一部分。

```python
from collections import Counter

class Solution:

    def topKFrequent(self, nums, k):
        counts = Counter(nums)
        max_count = max(counts.values())
        buckets = [[] for _ in range(max_count + 1)]
        for value, count in counts.items():
            buckets[count].append(value)
        answer = []
        for bucket in reversed(buckets):
            answer.extend(bucket)
            if len(answer) == k:
                return answer
```

**复杂度：** 时间及空间 \(O(n)\)，含统计表、桶和输出；\(n\) 为数组长度。

### 数据流的中位数（LeetCode 295）

困难 · [力扣原题](https://leetcode.cn/problems/find-median-from-data-stream/) · [灵茶山艾府题解](https://leetcode.cn/problems/find-median-from-data-stream/solutions/3015873/ru-he-zi-ran-yin-ru-da-xiao-dui-jian-ji-4v22k/)

#### 题面

实现 `MedianFinder`，让它能不断接收新整数，并在需要时返回目前全部数值的中位数。

`MedianFinder()` 创建空结构；`addNum(num)` 加入一个数；`findMedian()` 返回中位数。把已有数值排序后，数量为奇数时取中间项，为偶数时取中间两项的平均值。查询时至少已有一个数。

**数据范围与约定**

- `-10^5 <= num <= 10^5`
- 在调用 `findMedian` 之前，数据结构中至少有一个元素
- 最多 5 * 10^4 次调用 `addNum` 和 `findMedian`

**示例**

依次加入 `4、1、7`，中位数依次是 `4、2.5、4`；再加入 `2`，中位数变为 `3`。

#### 解法：用两个堆维护较小、较大两半

左堆保存较小的一半，能取出其中最大值；右堆保存较大的一半，能取出其中最小值。保持左堆与右堆等大，或左堆多一个。

两堆等大时，新数先进入右堆，再把右堆最小值转给左堆；左堆多一个时反过来。这样两侧仍有序且数量平衡，中位数可直接从堆顶读取。

```python
import heapq

class MedianFinder:

    def __init__(self):
        self.left = []
        self.right = []

    def addNum(self, num):
        if len(self.left) == len(self.right):
            smaller = heapq.heappushpop(self.right, num)
            heapq.heappush(self.left, -smaller)
        else:
            larger = -heapq.heappushpop(self.left, -num)
            heapq.heappush(self.right, larger)

    def findMedian(self):
        if len(self.left) > len(self.right):
            return -self.left[0]
        return (-self.left[0] + self.right[0]) / 2
```

**复杂度：** 插入 \(O(\log(q+1))\)，查询 \(O(1)\)，空间 \(O(q)\)；\(q\) 为已插入元素数。

**注意：** Python 最小堆用负数保存左半部；取左堆最大值时再取负号。


## 贪心算法

### 买卖股票的最佳时机（LeetCode 121）

简单 · [力扣原题](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/) · [灵茶山艾府题解](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/solutions/2464650/mei-ju-mai-chu-jie-ge-wei-hu-mai-ru-de-z-02ud/)

#### 题面

给定价格数组 `prices`，`prices[i]` 表示第 `i` 天的股票价格。你可以选择一天买入，再在之后的某一天卖出，最多完成这一笔交易。返回能够获得的最大利润。

买入必须早于卖出。如果怎样交易都不能赚钱，可以不交易，此时返回 0。

**数据范围与约定**

- `1 <= prices.length <= 10^5`
- `0 <= prices[i] <= 10^4`

**示例**

`[5,2,6,1,4]` 返回 `4`：以 `2` 买入、以之后的 `6` 卖出。

#### 解法：枚举卖出日，记录此前最低价

扫描每天价格，假设今天卖出，最好买入价就是此前最低价。用两者之差更新最大利润，再把今天价格纳入最低价。最大利润初始为零，因此一直亏损时返回零。

```python
class Solution:

    def maxProfit(self, prices):
        lowest = float('inf')
        best = 0
        for price in prices:
            best = max(best, price - lowest)
            lowest = min(lowest, price)
        return best
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为天数。

### 跳跃游戏（LeetCode 55）

中等 · [力扣原题](https://leetcode.cn/problems/jump-game/) · [灵茶山艾府题解](https://leetcode.cn/problems/jump-game/solutions/2798996/liang-chong-li-jie-fang-shi-wei-hu-zui-y-q67s/)

#### 题面

给定非负整数数组 `nums`，你最初站在下标 0。站在下标 `i` 时，可以向右跳跃，距离不超过 `nums[i]`。判断能否到达最后一个下标。

不必每次都跳允许的最远距离，可以选择更短的跳跃。只返回能否到达，不需要给出路径或跳跃次数。

**数据范围与约定**

- `1 <= nums.length <= 10^4`
- `0 <= nums[i] <= 10^5`

**示例**

`[2,0,0]` 可以一步到末尾，返回 `True`；`[1,0,1]` 会困在下标 `1`，返回 `False`。

#### 解法：维护目前最远能到哪里

从左到右扫描，记录已到达位置能跳到的最远下标。当前下标超过这个范围就失败；否则用当前位置更新最远距离。一旦覆盖终点即可成功。因为允许少跳几步，最远位置之前的所有位置也都可达。

```python
class Solution:

    def canJump(self, nums):
        farthest = 0
        for i, distance in enumerate(nums):
            if i > farthest:
                return False
            farthest = max(farthest, i + distance)
            if farthest >= len(nums) - 1:
                return True
        return True
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**写法补充：** 原文的另一版本在扫描结束后判断成功，仍维护同一个最远可达范围。

### 跳跃游戏 II（LeetCode 45）

中等 · [力扣原题](https://leetcode.cn/problems/jump-game-ii/) · [灵茶山艾府题解](https://leetcode.cn/problems/jump-game-ii/solutions/2926993/tu-jie-yi-zhang-tu-miao-dong-tiao-yue-yo-h2d4/)

#### 题面

给定非负整数数组 `nums`，你从下标 0 出发，站在下标 `i` 时可以向右跳最多 `nums[i]` 个位置。求到达最后一个下标至少需要跳几次。

题目保证最后一个位置一定能够到达。如果数组只有一个元素，已经位于终点，返回 0。

**数据范围与约定**

- `1 <= nums.length <= 10^4`
- `0 <= nums[i] <= 1000`
- 题目保证可以到达 n - 1

**示例**

`[2,1,2,1,1]` 返回 `2`，可走下标 `0→2→4`。

#### 解法：扫描当前跳数能覆盖的全部位置

`current_end` 是当前跳数能到达的最远下标。扫描它之前的所有位置，用 `next_end` 记录再跳一次最远能到哪里。扫描到当前边界时，增加一次跳跃，并把边界更新为 `next_end`。每轮都检查全部可选起跳点，因此不会多跳。

```python
class Solution:

    def jump(self, nums):
        jumps = 0
        current_end = next_end = 0
        for i in range(len(nums) - 1):
            next_end = max(next_end, i + nums[i])
            if i == current_end:
                jumps += 1
                current_end = next_end
        return jumps
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**注意：** 只扫描到终点前一位，避免到达终点后多计一次。

### 划分字母区间（LeetCode 763）

中等 · [力扣原题](https://leetcode.cn/problems/partition-labels/) · [灵茶山艾府题解](https://leetcode.cn/problems/partition-labels/solutions/2806706/ben-zhi-shi-he-bing-qu-jian-jian-ji-xie-ygsn8/)

#### 题面

给定字符串 `s`，把它从左到右切分成尽可能多的连续片段，使每种字母的全部出现都只落在其中一个片段里。返回各片段的长度，按原先后顺序排列。

每个字符都必须分到某一段，不能删除或重排。一个片段可以包含不同字母，但同一种字母不能被拆到两段里。

**数据范围与约定**

- `1 <= s.length <= 500`
- `s` 仅由小写英文字母组成

**示例**

`s="abac"` 返回 `[3,1]`，切成 `"aba"` 和 `"c"`，字母 `a` 没有被拆到不同片段。

#### 解法：覆盖当前片段中字母的最后一次出现

先记录每个字母最后出现的位置。扫描当前片段时，不断把右边界扩大到已见字母的最末位置。走到边界，说明这些字母以后都不会出现，可以立即切开。每次都在最早合法位置切分，片段数就最多。

```python
class Solution:

    def partitionLabels(self, s):
        last = {char: i for i, char in enumerate(s)}
        answer = []
        start = end = 0
        for i, char in enumerate(s):
            end = max(end, last[char])
            if i == end:
                answer.append(end - start + 1)
                start = i + 1
        return answer
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(26)\)，输出另计；\(n\) 为字符串长度，字符为小写字母。


## 动态规划

### 爬楼梯（LeetCode 70）

简单 · [力扣原题](https://leetcode.cn/problems/climbing-stairs/) · [灵茶山艾府题解](https://leetcode.cn/problems/climbing-stairs/solutions/2560716/jiao-ni-yi-bu-bu-si-kao-dong-tai-gui-hua-7zm1/)

#### 题面

一段楼梯共有 `n` 级，每次可以向上走 1 级或 2 级。从地面出发，求恰好到达第 `n` 级的不同走法数量。

每次走几级的先后顺序也属于方案的一部分，例如先走 1 级再走 2 级，与先走 2 级再走 1 级算两种走法。

**数据范围与约定**

- `1 <= n <= 45`

**示例**

`n=4` 返回 `5`，每次步长分别为 `1111、112、121、211、22`。

#### 解法：只保留前两级的方案数

到第 `i` 级的最后一步，只能从第 `i-1` 级走一步，或从第 `i-2` 级走两步，因此方案数等于前两项之和。用两个变量保存相邻两项，逐级更新即可。零级按“不移动”记一种方案，一级也有一种。

```python
class Solution:

    def climbStairs(self, n):
        previous, current = (1, 1)
        for _ in range(2, n + 1):
            previous, current = (current, previous + current)
        return current
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为台阶数。

#### 补充：直接递归（教学）

到第 i 级的最后一步来自 i−1 或 i−2，所以两种方案数相加；零级和一级都各有一种方案。同一剩余级数会在不同分支重复计算。

```python
class Solution:
    def climbStairs(self, n):
        # 此版本故意保留重复计算，用于说明递归关系
        def ways(steps):
            if steps <= 1:
                return 1
            return ways(steps - 1) + ways(steps - 2)
        return ways(n)
```

**复杂度：** 时间 \(O(\varphi^n)\)，φ≈1.618，递归栈 \(O(n)\)。

**注意：** 仅用于理解递归关系；较大输入会超时。

#### 补充：记忆化递归

到第 i 级的最后一步来自 i−1 或 i−2，所以两种方案数相加；零级和一级都各有一种方案。缓存相同 i 的返回值，避免重复求解。

```python
from functools import cache

class Solution:
    def climbStairs(self, n):
        @cache
        def ways(steps):
            if steps <= 1:
                return 1
            return ways(steps - 1) + ways(steps - 2)
        return ways(n)
```

**复杂度：** 时间 \(O(n)\)，缓存和递归栈 \(O(n)\)。

**注意：** 缓存消除重复计算，但递归栈仍需线性空间。

#### 补充：保存全部状态的一维递推

`ways[i]` 记录到达第 i 级的方法数。从小到大计算，每项等于前两项之和，计算时依赖已经就绪。

```python
class Solution:
    def climbStairs(self, n):
        ways = [1] * (n + 1)
        for steps in range(2, n + 1):
            ways[steps] = ways[steps - 1] + ways[steps - 2]
        return ways[n]
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** 主解法进一步只保留前两项。

#### 补充：矩阵快速幂

一次递推把相邻两项 `(a,b)` 变成 `(a+b,a)`，等价于乘矩阵 `[[1,1],[1,0]]`。从列向量 `[1,0]` 出发，需要做 `n` 次转移。反复把矩阵平方，可一次代表 1、2、4、8…次转移；按 `n` 的二进制位选取并相乘，只需对数次矩阵运算。

```python
def multiply(a, b):
    rows, columns, inner = len(a), len(b[0]), len(b)
    return [[sum(a[i][k] * b[k][j] for k in range(inner))
             for j in range(columns)] for i in range(rows)]

class Solution:
    def climbStairs(self, n):
        power = [[1, 1], [1, 0]]
        state = [[1], [0]]
        while n:
            if n & 1:
                state = multiply(power, state)
            power = multiply(power, power)
            n >>= 1
        return state[0][0]
```

**复杂度：** 本题整数范围内，时间 \(O(\log n)\)，额外空间 \(O(1)\)。

**注意：** 运算次数更少，但本题 `n`≤45，滚动变量版本更简单。

**写法补充：** 原文还给出并行赋值的滚动递推，以及 NumPy 矩阵快速幂，分别与上述对应方法相同。

### 杨辉三角（LeetCode 118）

简单 · [力扣原题](https://leetcode.cn/problems/pascals-triangle/) · [灵茶山艾府题解](https://leetcode.cn/problems/pascals-triangle/solutions/2784222/jian-dan-ti-jian-dan-zuo-pythonjavaccgoj-z596/)

#### 题面

给定正整数 `numRows`，返回杨辉三角的前 `numRows` 行，结果是二维列表，每个子列表对应一行。

第一行只有一个 1。之后每行比上一行多一个数，首尾都为 1，内部每个数等于上一行中它左上方与右上方两个数之和。

**数据范围与约定**

- `1 <= numRows <= 30`

**示例**

前四行为 `[[1],[1,1],[1,2,1],[1,3,3,1]]`，第四行两个 `3` 分别来自 `1+2` 和 `2+1`。

#### 解法：根据上一行构造下一行

每行先全部填成 `1`，首尾便符合要求。内部位置用上一行左上、右上两个值之和填写。上一行已经保存在答案中，可直接读取，不需要再建一张表。

```python
class Solution:

    def generate(self, numRows):
        answer = []
        for row_index in range(numRows):
            row = [1] * (row_index + 1)
            for col in range(1, row_index):
                row[col] = answer[-1][col - 1] + answer[-1][col]
            answer.append(row)
        return answer
```

**复杂度：** 时间 \(O(r^2)\)，额外空间 \(O(1)\)，输出空间 \(O(r^2)\)；\(r\) 为行数。

### 打家劫舍（LeetCode 198）

中等 · [力扣原题](https://leetcode.cn/problems/house-robber/) · [灵茶山艾府题解](https://leetcode.cn/problems/house-robber/solutions/2102725/ru-he-xiang-chu-zhuang-tai-ding-yi-he-zh-1wt1/)

#### 题面

房屋沿一条直线排列，数组 `nums` 的每一项表示对应房屋里的金额。你可以选择一些房屋，但不能同时选择相邻的两间，否则会触发警报。返回最多能够取得的总金额。

每间房屋至多选择一次，也可以跳过任意房屋。首尾两间不额外相邻，这里不是环形排列。

**数据范围与约定**

- `1 <= nums.length <= 100`
- `0 <= nums[i] <= 400`

**示例**

`[3,2,5,1]` 返回 `8`，选择第一、第三间房，金额为 `3+5`。

#### 解法：比较选当前房屋和不选两种情况

不选当前房屋，就沿用前一间处理完的最大金额；选当前房屋，就必须跳过前一间，把当前金额加到前两间处理完的最大金额上。每次取两者较大值，用两个变量保存所需的历史结果。

```python
class Solution:

    def rob(self, nums):
        two_back = one_back = 0
        for value in nums:
            two_back, one_back = (one_back, max(one_back, two_back + value))
        return one_back
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为房屋数量。

#### 补充：记忆化：最后一间偷或不偷

`best(last)` 表示从第一间到下标 `last` 的房屋最多能取多少。不选当前间，用前一项；选它，用前两项加当前金额。取两者较大值，并缓存每个 `last` 的结果，避免重复计算。

```python
from functools import cache

class Solution:
    def rob(self, nums):
        @cache
        def best(last):
            if last < 0:
                return 0
            return max(best(last - 1), best(last - 2) + nums[last])
        return best(len(nums) - 1)
```

**复杂度：** 时间 \(O(n)\)，缓存和递归栈 \(O(n)\)。

#### 补充：保存全部状态的一维递推

数组前面留两个零，统一处理没有房子的边界。处理第 i 间时，在不偷它的上一项与偷它加上前前项之间取最大值。

```python
class Solution:
    def rob(self, nums):
        best = [0] * (len(nums) + 2)
        for index, money in enumerate(nums):
            best[index + 2] = max(best[index + 1], best[index] + money)
        return best[-1]
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** 主解法只保留依赖的两个状态，省去数组。

### 完全平方数（LeetCode 279）

中等 · [力扣原题](https://leetcode.cn/problems/perfect-squares/) · [灵茶山艾府题解](https://leetcode.cn/problems/perfect-squares/solutions/2830762/dong-tai-gui-hua-cong-ji-yi-hua-sou-suo-3kz1g/)

#### 题面

给定正整数 `n`，把它写成若干个完全平方数的和，返回最少需要多少个数。完全平方数是某个整数与自身相乘得到的数，例如 1、4、9、16。

同一个平方数可以重复使用。例如 8 可以写成 4+4，需要两个数；只返回最少个数，不需要返回具体组合。

**数据范围与约定**

- `1 <= n <= 10^4`

**示例**

`n=13` 返回 `2`，因为 `13=9+4`，不能只用一个平方数表示。

#### 解法：提前计算所有金额的最少个数

`SQUARE_COUNTS[total]` 表示凑出 `total` 至少需要几个平方数。依次枚举平方数，从小到大更新总和：比较原答案与“少一个当前平方数的答案再加一”。从小到大更新，允许同一平方数重复使用。

表按题目上界预先算一次，后续调用直接查表。

```python
from math import isqrt
SQUARE_LIMIT = 10000
SQUARE_COUNTS = [0] + [float('inf')] * SQUARE_LIMIT
for base in range(1, isqrt(SQUARE_LIMIT) + 1):
    square = base * base
    for total in range(square, SQUARE_LIMIT + 1):
        candidate = SQUARE_COUNTS[total - square] + 1
        SQUARE_COUNTS[total] = min(SQUARE_COUNTS[total], candidate)

class Solution:

    def numSquares(self, n):
        return SQUARE_COUNTS[n]
```

**复杂度：** 令预计算上界 \(U=10000\)，建立表的时间为 \(O(U\sqrt U)\)，空间为 \(O(U)\)。表建立后，每次 `numSquares` 查询为 \(O(1)\)。

**注意：** 提交时要包括 `Solution` 类前的预计算代码。

#### 补充：共享缓存的完全背包递归

`square_count(limit, total)` 表示只用从 1 到 `limit` 的整数各自的平方，凑出 `total` 至少需要几个数。不选当前平方数就减小 `limit`；选它就减少 `total`，仍保留 `limit` 以便重复使用。函数位于类外，缓存可供后续调用复用。

```python
from functools import cache
from math import inf, isqrt

@cache
def square_count(limit, total):
    if limit == 0:
        return 0 if total == 0 else inf
    square = limit * limit
    if total < square:
        return square_count(limit - 1, total)
    return min(square_count(limit - 1, total), square_count(limit, total - square) + 1)

class Solution:
    def numSquares(self, n):
        return square_count(isqrt(n), n)
```

**复杂度：** 首次计算上界时间、缓存 \(O(n\sqrt{n})\)，递归深度最坏 \(O(n)\)；后续同一状态可直接命中缓存。

**注意：** 缓存跨调用保留；递归深度较大时受运行环境限制。

#### 补充：预先计算完整二维表

表的行表示允许使用到哪个平方数，列表示目标和。当前行要么沿用上一行，要么用一个当前平方数，加上当前行较小目标的答案。按题目上界一次预计算，之后查询对应表格位置。

```python
from math import inf, isqrt

UPPER = 10000
TABLE = [[inf] * (UPPER + 1) for _ in range(isqrt(UPPER) + 1)]
TABLE[0][0] = 0
for limit in range(1, len(TABLE)):
    square = limit * limit
    for total in range(UPPER + 1):
        TABLE[limit][total] = TABLE[limit - 1][total]
        if total >= square:
            TABLE[limit][total] = min(TABLE[limit][total], TABLE[limit][total - square] + 1)

class Solution:
    def numSquares(self, n):
        return TABLE[isqrt(n)][n]
```

**复杂度：** 设题目上界 U=10000，预处理时间、空间 \(O(U\sqrt{U})\)，每次查询 \(O(1)\)。

**注意：** 表在类外只计算一次；主解法把它压成一行以减少空间。

#### 补充：广度优先搜索最少使用次数

从和零出发，每次加一个平方数。按使用个数逐层扩展，第一次到达 `n` 就找到了最少个数。某个和加入下一层时立即标记，保证它只被处理一次。

```python
class Solution:
    def numSquares(self, n):
        layer = [0]
        visited = [True] + [False] * n
        steps = 0
        while layer:
            following = []
            for total in layer:
                if total == n:
                    return steps
                root = 1
                while total + root * root <= n:
                    value = total + root * root
                    if not visited[value]:
                        visited[value] = True
                        following.append(value)
                    root += 1
            layer = following
            steps += 1
```

**复杂度：** 时间 \(O(n\sqrt{n})\)，空间 \(O(n)\)。

**注意：** 每次调用进行搜索，不做全局预计算。

### 零钱兑换（LeetCode 322）

中等 · [力扣原题](https://leetcode.cn/problems/coin-change/) · [灵茶山艾府题解](https://leetcode.cn/problems/coin-change/solutions/2119065/jiao-ni-yi-bu-bu-si-kao-dong-tai-gui-hua-21m5/)

#### 题面

给定硬币面值数组 `coins` 和目标金额 `amount`，每种硬币都可以使用任意多枚。求恰好凑出 `amount` 所需的最少硬币枚数。

如果无法凑出目标金额，返回 `-1`；目标金额为 0 时返回 0。返回的是最少枚数，不是不同凑法的数量。

**数据范围与约定**

- `1 <= coins.length <= 12`
- `1 <= coins[i] <= 2^31 - 1`
- `0 <= amount <= 10^4`

**示例**

`coins=[2,5]`、`amount=9`，返回 `3`，对应 `5+2+2`；目标为 `3` 时返回 `-1`。

#### 解法：按金额递增更新最少硬币数

`best[total]` 记录凑出金额 `total` 的最少枚数，金额零为零，其余先设成表示不可达的大值。处理硬币 `coin` 时，用 `best[total-coin]+1` 尝试改进答案。金额从小到大更新，已经用过这枚硬币的较小金额还能继续使用它。

```python
class Solution:

    def coinChange(self, coins, amount):
        best = [amount + 1] * (amount + 1)
        best[0] = 0
        for coin in coins:
            for total in range(coin, amount + 1):
                best[total] = min(best[total], best[total - coin] + 1)
        return -1 if best[amount] > amount else best[amount]
```

**复杂度：** 时间 \(O(kA)\)，额外空间 \(O(A)\)；\(k\) 为硬币种类数，\(A\) 为目标金额。

#### 补充：记忆化完全背包

`best(index, total)` 表示只用下标不超过 `index` 的硬币凑 `total`，至少需要多少枚。不选当前币就减小 `index`；选一枚后只减少 `total`，仍可继续选同种币。没有硬币可选时，只有金额零能成功。

```python
from functools import cache
from math import inf

class Solution:
    def coinChange(self, coins, amount):
        @cache
        def best(index, total):
            if index < 0:
                return 0 if total == 0 else inf
            if total < coins[index]:
                return best(index - 1, total)
            return min(best(index - 1, total), best(index, total - coins[index]) + 1)
        answer = best(len(coins) - 1, amount)
        return answer if answer < inf else -1
```

**复杂度：** 时间与缓存 \(O(kA)\)，递归深度上界 \(O(k+A/\min(\text{coins}))\)，A 为金额、k 为种数。

**注意：** 递归使用同一种硬币时不减少 `index`，这是与每个元素只能选一次的背包区别。

#### 补充：二维完全背包表

第 i 行代表只使用前 i 种硬币。处理当前硬币时，不选从上一行取值，选则从当前行较小金额取值加一。金额递增遍历，允许当前硬币反复使用。

```python
from math import inf

class Solution:
    def coinChange(self, coins, amount):
        dp = [[inf] * (amount + 1) for _ in range(len(coins) + 1)]
        dp[0][0] = 0
        for row, coin in enumerate(coins, 1):
            for total in range(amount + 1):
                dp[row][total] = dp[row - 1][total]
                if total >= coin:
                    dp[row][total] = min(dp[row][total], dp[row][total - coin] + 1)
        answer = dp[-1][amount]
        return answer if answer < inf else -1
```

**复杂度：** 时间 \(O(kA)\)，空间 \(O(kA)\)。

#### 补充：两个数组轮流保存相邻两行

当前状态只依赖上一行同一金额、当前行较小金额，所以保留两行即可。每轮完整覆盖当前行，金额仍必须递增，确保当前行的小金额已更新。

```python
from math import inf

class Solution:
    def coinChange(self, coins, amount):
        rows = [[inf] * (amount + 1) for _ in range(2)]
        rows[0][0] = 0
        for index, coin in enumerate(coins):
            previous, current = rows[index % 2], rows[(index + 1) % 2]
            for total in range(amount + 1):
                current[total] = previous[total]
                if total >= coin:
                    current[total] = min(current[total], current[total - coin] + 1)
        answer = rows[len(coins) % 2][amount]
        return answer if answer < inf else -1
```

**复杂度：** 时间 \(O(kA)\)，空间 \(O(A)\)。

**注意：** 主解法继续合并成一个数组。两行和一行的渐进空间相同。

#### 补充：广度优先搜索金额

从金额 0 出发，每条边表示再选一枚硬币。按使用硬币数逐层扩展，第一次达到 `amount` 就是最少枚数。只处理不超过目标且从未入队的金额；队列耗尽则无解。

```python
class Solution:
    def coinChange(self, coins, amount):
        layer = [0]
        seen = [True] + [False] * amount
        count = 0
        while layer:
            following = []
            for total in layer:
                if total == amount:
                    return count
                for coin in coins:
                    value = total + coin
                    if value <= amount and not seen[value]:
                        seen[value] = True
                        following.append(value)
            layer = following
            count += 1
        return -1
```

**复杂度：** 时间 \(O(kA)\)，空间 \(O(A)\)。

**注意：** 每增加一枚硬币就走一层，属于求最少步数的搜索。

### 单词拆分（LeetCode 139）

中等 · [力扣原题](https://leetcode.cn/problems/word-break/) · [灵茶山艾府题解](https://leetcode.cn/problems/word-break/solutions/2968135/jiao-ni-yi-bu-bu-si-kao-dpcong-ji-yi-hua-chrs/)

#### 题面

给定字符串 `s` 和单词列表 `wordDict`，判断能否从字典中选择若干单词，按顺序拼接后恰好得到整个 `s`。

同一个字典单词可以重复使用，不要求用完字典中的全部单词。不能跳过或重排 `s` 中的字符，只返回布尔值。

**数据范围与约定**

- `1 <= s.length <= 300`
- `1 <= wordDict.length <= 1000`
- `1 <= wordDict[i].length <= 20`
- `s 和 wordDict[i] 仅由小写英文字母组成`
- `wordDict` 中的所有字符串 互不相同

**示例**

`s="applepenapple"`、`wordDict=["apple","pen"]`，返回 `True`，可拆为 `"apple"+"pen"+"apple"`。

#### 解法：判断每个前缀能否拆分

`possible[end]` 表示前 `end` 个字符能否拆成字典单词。枚举最后一段的起点 `start`：前面的前缀可拆，且 `s[start:end]` 在字典中，当前前缀就可拆。最后一段不会长于字典最长单词，因此只向左检查这个范围。

```python
class Solution:

    def wordBreak(self, s, wordDict):
        max_length = max(map(len, wordDict))
        words = set(wordDict)
        possible = [False] * (len(s) + 1)
        possible[0] = True
        for end in range(1, len(s) + 1):
            lower = max(end - max_length - 1, -1)
            for start in range(end - 1, lower, -1):
                if possible[start] and s[start:end] in words:
                    possible[end] = True
                    break
        return possible[-1]
```

**复杂度：** 时间上界 \(O(D+nL^2)\)，空间 \(O(D+n)\)；\(D\) 为词典总字符数，\(n\) 为串长，\(L\) 为最长词长，计入子串复制和哈希。

#### 补充：记忆化拆分前缀

`possible(end)` 判断前 `end` 个字符能否拆分。枚举最后一个单词的起点，若该段在字典中且前缀可拆分，就成功。最后单词不可能长于字典最长单词，因此限制枚举范围。

```python
from functools import cache

class Solution:
    def wordBreak(self, s, wordDict):
        words = set(wordDict)
        longest = max(map(len, wordDict))
        @cache
        def possible(end):
            if end == 0:
                return True
            for begin in range(end - 1, max(-1, end - longest - 1), -1):
                if s[begin:end] in words and possible(begin):
                    return True
            return False
        return possible(len(s))
```

**复杂度：** 时间上界 \(O(D+nL^2)\)，空间 \(O(D+n)\)；D 为词典总字符数，n 为串长，L 为最长词长。

**注意：** 子串切片及其哈希计算也需时间，不能把每次字典查询整体当作常数操作。

**写法补充：** 原文的 `for` 提前返回与 `any` 写法检查相同的候选单词。

### 最长递增子序列（LeetCode 300）

中等 · [力扣原题](https://leetcode.cn/problems/longest-increasing-subsequence/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-increasing-subsequence/solutions/2147040/jiao-ni-yi-bu-bu-si-kao-dpfu-o1-kong-jia-4zma/)

#### 题面

给定整数数组 `nums`，从中选择一些元素，保留它们在原数组中的先后顺序，使选出的数严格递增。返回最多能选出多少个元素。

选出的元素不必相邻，但不能改变相对顺序。严格递增表示每个数都大于前一个，相等的数不能连续选入同一递增序列。

**数据范围与约定**

- `1 <= nums.length <= 2500`
- `-10^4 <= nums[i] <= 10^4`

**进阶要求**

- 你能将算法的时间复杂度降低到 \(O(n \log(n))\) 吗?

**示例**

`[3,1,4,2,5]` 返回 `3`，可选子序列 `[1,2,5]`，也可选 `[3,4,5]`。

#### 解法：二分维护每种长度的最小结尾

`tails[i]` 是长度为 `i+1` 的递增子序列能达到的最小结尾。相同长度下，结尾越小，后面越容易接上新数。对当前值，二分找第一个不小于它的结尾并替换；若比所有结尾都大，就追加一项，最长长度加一。

```python
from bisect import bisect_left

class Solution:

    def lengthOfLIS(self, nums):
        tails = []
        for value in nums:
            index = bisect_left(tails, value)
            if index == len(tails):
                tails.append(value)
            else:
                tails[index] = value
        return len(tails)
```

**复杂度：** 时间 \(O(n\log n)\)，辅助空间 \(O(n)\)；\(n\) 为数组长度，采用额外数组写法。

**注意：** `tails` 各项未必来自同一条子序列，只用其长度作为答案。

#### 补充：记忆化计算每个结尾的最长长度

`ending(index)` 表示以下标 `index` 结尾的最长递增子序列。枚举它前面所有更小的值，取对应长度的最大值再加一；没有更小值时，长度为一。缓存每个结尾的结果，最后取最大值。

```python
from functools import cache

class Solution:
    def lengthOfLIS(self, nums):
        @cache
        def ending(index):
            previous = 0
            for pos in range(index):
                if nums[pos] < nums[index]:
                    previous = max(previous, ending(pos))
            return previous + 1
        return max(ending(index) for index in range(len(nums)))
```

**复杂度：** 时间 \(O(n^2)\)，缓存和递归栈 \(O(n)\)。

**注意：** 便于理解状态；二分维护最小结尾的方法渐进更快。

#### 补充：枚举前驱的一维递推

按结尾位置从左到右计算。每个位置检查所有更早且更小的元素，把其中最长长度加一；若找不到，当前数自身构成长为一的序列。

```python
class Solution:
    def lengthOfLIS(self, nums):
        ending = [0] * len(nums)
        for index, value in enumerate(nums):
            for pos, earlier in enumerate(nums[:index]):
                if earlier < value:
                    ending[index] = max(ending[index], ending[pos])
            ending[index] += 1
        return max(ending)
```

**复杂度：** 时间 \(O(n^2)\)，空间 \(O(n)\)。

**注意：** 这份写法会临时复制已处理前缀，峰值辅助空间仍为线性。

#### 补充：在输入前缀中维护各长度的最小结尾

`nums` 的前 `length` 项充当结尾数组，第 j 项表示长为 j+1 的递增子序列能达到的最小结尾。对当前值找第一个不小于它的位置并替换；若没有，则延长。写入位置不超过当前扫描位置，不会破坏未读取数据。

```python
from bisect import bisect_left

class Solution:
    def lengthOfLIS(self, nums):
        length = 0
        for value in nums:
            position = bisect_left(nums, value, 0, length)
            nums[position] = value
            if position == length:
                length += 1
        return length
```

**复杂度：** 时间 \(O(n \log n)\)，额外空间 \(O(1)\)。

**注意：** 会修改 `nums`；工作区各项未必属于同一条实际子序列，只用于求长度。

### 乘积最大子数组（LeetCode 152）

中等 · [力扣原题](https://leetcode.cn/problems/maximum-product-subarray/) · [灵茶山艾府题解](https://leetcode.cn/problems/maximum-product-subarray/solutions/2968916/dong-tai-gui-hua-jian-ji-gao-xiao-python-i778/)

#### 题面

给定整数数组 `nums`，选择一段非空连续子数组，使这一段中所有数相乘的结果最大。返回这个最大乘积。

数组可能包含正数、负数和零。所选元素必须连续，不能跳过不想要的元素，也不能选择空数组。

**数据范围与约定**

- `1 <= nums.length <= 2 * 10^4`
- `-10 <= nums[i] <= 10`
- `nums` 的任何子数组的乘积都 保证 是一个 32-位 整数

**示例**

`[-2,3,-4]` 返回 `24`，最大乘积来自整个数组。

#### 解法：同时记录以当前数结尾的最大积和最小积

负数可能把最小负积变成最大正积，所以两个极值都要保留。读到一个新数时，分别比较它单独成段、接在旧最大积后、接在旧最小积后三种结果，更新两个极值。答案是所有结尾的最大积中的最大值。

```python
class Solution:

    def maxProduct(self, nums):
        largest = smallest = answer = nums[0]
        for index in range(1, len(nums)):
            value = nums[index]
            a, b = (value * largest, value * smallest)
            largest = max(value, a, b)
            smallest = min(value, a, b)
            answer = max(answer, largest)
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

**注意：** 两个新极值都必须由旧状态计算，不能让先更新的值影响另一个。

#### 补充：同时保存每个结尾的最大积和最小积

负数相乘会交换大小关系，因此仅存最大积不够。每个结尾都比较三种选择：当前数单独成段、接在上一最大积后、接在上一最小积后。分别取最大和最小，答案取所有最大积中的最大值。

```python
class Solution:
    def maxProduct(self, nums):
        high, low = [nums[0]], [nums[0]]
        for index in range(1, len(nums)):
            value = nums[index]
            choices = (value, value * high[-1], value * low[-1])
            high.append(max(choices))
            low.append(min(choices))
        return max(high)
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

#### 补充：负数时先交换最大积与最小积

若当前数为负，原最大积乘它后会变小，原最小积乘它后会变大，先交换两者再更新。这样最大积只需比较继续接上和当前数独立成段两种选择，最小积同理。

```python
class Solution:
    def maxProduct(self, nums):
        high = low = 1
        answer = nums[0]
        for value in nums:
            if value < 0:
                high, low = low, high
            high = max(value, high * value)
            low = min(value, low * value)
            answer = max(answer, high)
        return answer
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 与同时比较三项的滚动版本同阶，但利用符号关系减少候选项。

### 分割等和子集（LeetCode 416）

中等 · [力扣原题](https://leetcode.cn/problems/partition-equal-subset-sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/partition-equal-subset-sum/solutions/2785266/0-1-bei-bao-cong-ji-yi-hua-sou-suo-dao-d-ev76/)

#### 题面

给定正整数数组 `nums`，判断能否把其中全部元素分成两组，使两组元素的总和相等。

每个数组位置必须分到其中一组，而且只能使用一次。只返回是否能够这样分组，不需要返回两个组的具体内容。

**数据范围与约定**

- `1 <= nums.length <= 200`
- `1 <= nums[i] <= 100`

**示例**

`[1,2,3,4]` 返回 `True`，可分成 `[1,4]` 与 `[2,3]`；`[1,2,4]` 总和为奇数，返回 `False`。

#### 解法：倒序更新可凑出的和

总和为奇数时直接失败；否则只需找出和为总和一半的子集。`possible[amount]` 记录金额是否可达，初始只有零可达。加入一个数时从大到小更新，确保读取的仍是加入它之前的结果，每个元素只使用一次。

只扫描已处理元素总和能够覆盖的范围；目标一旦可达就立即成功。

```python
class Solution:

    def canPartition(self, nums):
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        possible = [False] * (target + 1)
        possible[0] = True
        upper = 0
        for value in nums:
            upper = min(upper + value, target)
            for amount in range(upper, value - 1, -1):
                possible[amount] = possible[amount] or possible[amount - value]
            if possible[target]:
                return True
        return False
```

**复杂度：** 时间 \(O(nT)\)，辅助空间 \(O(T)\)；\(n\) 为元素数，\(T\) 为总和一半。

#### 补充：记忆化的选或不选

总和为奇数必然失败。否则寻找和为总和一半的子集；选当前数或不选，都进入前一个下标，确保每个元素至多使用一次。缓存下标和剩余目标的组合。

```python
from functools import cache

class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2:
            return False
        @cache
        def possible(index, remaining):
            if index < 0:
                return remaining == 0
            if remaining < nums[index]:
                return possible(index - 1, remaining)
            return possible(index - 1, remaining - nums[index]) or possible(index - 1, remaining)
        return possible(len(nums) - 1, total // 2)
```

**复杂度：** 时间、缓存 \(O(nT)\)，递归栈 \(O(n)\)；T 为总和一半。

#### 补充：二维布尔背包

`dp[row][amount]` 表示前 `row` 个数能否凑出 `amount`。不选当前数就读上一行同列，选它就读上一行减去当前数的列。两种选择都读上一行，保证当前数只使用一次。

```python
class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        dp = [[False] * (target + 1) for _ in range(len(nums) + 1)]
        dp[0][0] = True
        for row, value in enumerate(nums, 1):
            for amount in range(target + 1):
                dp[row][amount] = (amount >= value and dp[row - 1][amount - value]) or dp[row - 1][amount]
        return dp[-1][target]
```

**复杂度：** 时间、空间 \(O(nT)\)，T 为总和一半。

**注意：** 空间优化版用一行，并从大到小更新金额，以保留上一行的信息。

#### 补充：用大整数的二进制位保存可达的和

`bits` 的第 j 个二进制位为一，表示能凑出和 j。初始只有和零可达，所以设为 1。加入 `value` 时，把旧 `bits` 左移 `value` 位，得到选它后的所有新和；再按位或上旧 `bits`，保留不选的情况。最后检查目标位。

```python
class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2:
            return False
        bits = 1
        for value in nums:
            bits |= bits << value
        return ((bits >> (total // 2)) & 1) == 1
```

**复杂度：** 设总和 S、机器字位数 w，时间 \(O(n\lceil S/w\rceil )\)，空间 \(O(\lceil S/w\rceil )\) 个机器字；Python 大整数位运算不是 \(O(1)\)。

**注意：** 一次位运算同时更新许多可达状态，但大整数越长，运算成本也越高。

**写法补充：** 记忆化版本还可合并布尔判断条件，选或不选的递归不变。

### 最长有效括号（LeetCode 32）

困难 · [力扣原题](https://leetcode.cn/problems/longest-valid-parentheses/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-valid-parentheses/solutions/3843096/on-chai-zha-dan-tong-guo-li-zi-fa-ming-s-lb5s/)

#### 题面

给定只包含 `(` 和 `)` 的字符串 `s`，找出最长的一段连续子串，使其中所有括号都能正确匹配，返回这段子串的长度。

不能跳过字符拼接答案。若不存在任何非空有效括号段，返回 0；例如 `)()()` 中最长有效部分为 `()()`，长度是 4。

**数据范围与约定**

- `0 <= s.length <= 3 * 10^4`
- `s[i] 为 '(' 或 ')'`

**示例**

`s=")()()"` 返回 `4`，最长有效子串是末尾的 `"()()"`。

#### 解法：下标栈记录有效段之前的边界

栈底先放边界 `-1`，遇到左括号就压入其下标。遇到右括号先弹栈：若栈仍非空，当前下标减去栈顶，就是以它结尾的最长有效长度；若栈空，说明这个右括号多余，把它的下标压入，作为下一段的新边界。

```python
class Solution:

    def longestValidParentheses(self, s):
        stack = [-1]
        best = 0
        for i, char in enumerate(s):
            if char == '(':
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    best = max(best, i - stack[-1])
        return best
```

**复杂度：** 时间 \(O(n)\)，辅助空间 \(O(n)\)；\(n\) 为字符串长度。

#### 补充：栈配对后找最长连续标记

从左到右用栈保存未配对左括号，遇到右括号就与最近左括号配对，并标记两个位置。未配对位置会打断合法段，最长连续标记段就是答案。

```python
class Solution:
    def longestValidParentheses(self, s):
        paired = [False] * len(s)
        openings = []
        for index, char in enumerate(s):
            if char == '(':
                openings.append(index)
            elif openings:
                paired[index] = paired[openings.pop()] = True
        best = length = 0
        for valid in paired:
            length = length + 1 if valid else 0
            best = max(best, length)
        return best
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

#### 补充：正反两遍计数

正向扫描时统计左右括号，相等就得到合法段；右括号更多时，这段无法补救，清零重新开始。正向可能漏掉左括号过多的尾段，所以再反向扫描，并交换左右括号角色。

```python
class Solution:
    def longestValidParentheses(self, s):
        def scan(chars, opening):
            opened = closed = best = 0
            for char in chars:
                if char == opening:
                    opened += 1
                else:
                    closed += 1
                if closed > opened:
                    opened = closed = 0
                elif opened == closed:
                    best = max(best, 2 * closed)
            return best
        return max(scan(s, '('), scan(reversed(s), ')'))
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)。

**注意：** 使用 `reversed` 迭代而非 `s[::-1]` 复制字符串，才能保留常数辅助空间。


## 多维动态规划

### 不同路径（LeetCode 62）

中等 · [力扣原题](https://leetcode.cn/problems/unique-paths/) · [灵茶山艾府题解](https://leetcode.cn/problems/unique-paths/solutions/3062432/liang-chong-fang-fa-dong-tai-gui-hua-zu-o5k32/)

#### 题面

有一个 `m` 行、`n` 列的网格。机器人从左上角出发，每次只能向右或向下移动一个格子，目标是右下角。返回不同移动路径的数量。

网格没有障碍物。路径只要在某一步的方向不同，就算不同走法；不能向左、向上或斜着移动。

**数据范围与约定**

- `1 <= m, n <= 100`
- 题目数据保证答案小于等于 2 * 10^9

**示例**

`m=2`、`n=4` 返回 `4`：唯一一次向下可以发生在四列中的任意一列。

#### 解法：用一行数组累加路径数

到达当前格子的最后一步只能来自上方或左方。逐行从左到右更新：`paths[col]` 的旧值是上方路径数，已经更新的 `paths[col-1]` 是左方路径数，两者相加后写回。首行每格都只有一直向右这一种走法，初始值全部设为一。

```python
class Solution:

    def uniquePaths(self, m, n):
        paths = [1] * n
        for _ in range(1, m):
            for col in range(1, n):
                paths[col] += paths[col - 1]
        return paths[-1]
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(n)\)；\(m,n\) 为行列数。

#### 补充：记忆化递归统计路径

到一个格子的最后一步只能来自上方或左方，所以路径数相加。起点有一种走法，越界位置没有走法。缓存每个坐标，避免重复计算。

```python
from functools import cache

class Solution:
    def uniquePaths(self, m, n):
        @cache
        def ways(row, column):
            if row < 0 or column < 0:
                return 0
            if row == 0 and column == 0:
                return 1
            return ways(row - 1, column) + ways(row, column - 1)
        return ways(m - 1, n - 1)
```

**复杂度：** 时间和缓存 \(O(mn)\)，递归栈 \(O(m+n)\)。

#### 补充：二维路径数表

额外留一行、一列零处理越界。起点设为一，其余格子等于上方和左方之和；从上到下、从左到右填表即可。

```python
class Solution:
    def uniquePaths(self, m, n):
        ways = [[0] * (n + 1) for _ in range(m + 1)]
        for row in range(1, m + 1):
            for column in range(1, n + 1):
                if row == column == 1:
                    ways[row][column] = 1
                else:
                    ways[row][column] = ways[row - 1][column] + ways[row][column - 1]
        return ways[m][n]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(mn)\)。

**注意：** 主解法只保留一行。

#### 补充：组合数直接计数

任何路径都要向下 `m`−1 次、向右 `n`−1 次。共 `m`+`n`−2 步中，选出 `m`−1 个位置向下，其他位置就只能向右，因此直接计算这个组合数即可。

```python
from math import comb

class Solution:
    def uniquePaths(self, m, n):
        return comb(m + n - 2, m - 1)
```

**复杂度：** 按逐项乘除计算，为 \(O(\min(m,n))\) 次整数运算，保存常数个整数；大整数成本随位数增长。

**注意：** 这里使用 `math.comb` 计算组合数。

**写法补充：** 递归和二维表各有不同的边界初始化写法；组合数也可逐项乘除计算，需使用整数除法。

### 最小路径和（LeetCode 64）

中等 · [力扣原题](https://leetcode.cn/problems/minimum-path-sum/) · [灵茶山艾府题解](https://leetcode.cn/problems/minimum-path-sum/solutions/3045828/jiao-ni-yi-bu-bu-si-kao-dpcong-ji-yi-hua-zfb2/)

#### 题面

给定由非负整数组成的网格 `grid`，从左上角走到右下角，每次只能向右或向下移动一格。求经过格子上的数值总和的最小值。

总和包含起点和终点的数值。只返回最小总和，不需要返回具体路径。

**数据范围与约定**

- `m == grid.length`
- `n == grid[i].length`
- `1 <= m, n <= 200`
- `0 <= grid[i][j] <= 200`

**示例**

`[[1,4,1],[2,1,1]]` 返回 `5`，路径为下、右、右，经过 `1、2、1、1`。

#### 解法：用一行数组保存最小路径和

每个格子的答案是“上方与左方答案中较小的一个，再加当前格子值”。逐行从左到右更新时，数组旧值对应上方，新左邻对应左方，因此只需一行存储。起点设置初值，越界方向按无穷处理，避免选到不存在的路线。

```python
class Solution:

    def minPathSum(self, grid):
        cols = len(grid[0])
        best = [float('inf')] * cols
        best[0] = 0
        for row in grid:
            for j, value in enumerate(row):
                left = best[j - 1] if j else float('inf')
                best[j] = min(best[j], left) + value
        return best[-1]
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(n)\)；\(m,n\) 为网格行列数。

#### 补充：直接递归最小路径和（教学）

到达当前格子前只能在左边或上边，取两种最小路径和中较小的，再加当前值。越界返回无穷，起点直接返回自己的数值。重复求解相同格子会产生大量重复工作。

```python
from math import inf

class Solution:
    def minPathSum(self, grid):
        # 教学版本：没有缓存
        def cost(row, column):
            if row < 0 or column < 0:
                return inf
            if row == 0 and column == 0:
                return grid[0][0]
            return grid[row][column] + min(cost(row, column - 1), cost(row - 1, column))
        return cost(len(grid) - 1, len(grid[0]) - 1)
```

**复杂度：** 时间上界 \(O(2^{m+n})\)，递归栈 \(O(m+n)\)。

**注意：** 仅用于理解递归关系；较大输入会超时。

#### 补充：记忆化最小路径和

到达当前格子前只能在左边或上边，取两种最小路径和中较小的，再加当前值。越界返回无穷，起点直接返回自己的数值。缓存坐标结果，消除重复子问题。

```python
from math import inf
from functools import cache

class Solution:
    def minPathSum(self, grid):
        @cache
        def cost(row, column):
            if row < 0 or column < 0:
                return inf
            if row == 0 and column == 0:
                return grid[0][0]
            return grid[row][column] + min(cost(row, column - 1), cost(row - 1, column))
        return cost(len(grid) - 1, len(grid[0]) - 1)
```

**复杂度：** 时间和缓存 \(O(mn)\)，递归栈 \(O(m+n)\)。

**注意：** 保留输入矩阵。

#### 补充：二维最小路径和表

表外侧一行、一列填无穷，避免错误选择越界路线。起点单独赋值，其余格子取上方和左方较小的路径和，加当前格子值。

```python
from math import inf

class Solution:
    def minPathSum(self, grid):
        rows, columns = len(grid), len(grid[0])
        cost = [[inf] * (columns + 1) for _ in range(rows + 1)]
        for row in range(rows):
            for column in range(columns):
                if row == column == 0:
                    cost[1][1] = grid[0][0]
                else:
                    cost[row + 1][column + 1] = grid[row][column] + min(cost[row][column + 1], cost[row + 1][column])
        return cost[rows][columns]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(mn)\)。

#### 补充：借用 grid 第一行保存滚动状态

`state` 直接指向 `grid[0]`，先把它改成第一行的累计和。再处理后续行：`state[column]` 的旧值代表上方，新 `state[column-1]` 代表左方，取较小者加当前值。

```python
class Solution:
    def minPathSum(self, grid):
        state = grid[0]
        for column in range(1, len(state)):
            state[column] += state[column - 1]
        for row in range(1, len(grid)):
            state[0] += grid[row][0]
            for column in range(1, len(state)):
                state[column] = min(state[column], state[column - 1]) + grid[row][column]
        return state[-1]
```

**复杂度：** 时间 \(O(mn)\)，额外空间 \(O(1)\)。

**注意：** 只把第一行当工作数组改写，其他行保持原值。

**写法补充：** 二维表另有设置虚拟入口的初始化写法，仍取上方与左方的较小值。

### 最长回文子串（LeetCode 5）

中等 · [力扣原题](https://leetcode.cn/problems/longest-palindromic-substring/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-palindromic-substring/solutions/2958179/mo-ban-on-manacher-suan-fa-pythonjavacgo-t6cx/)

#### 题面

给定字符串 `s`，返回其中最长的连续回文子串。回文的意思是这一段字符从左向右读和从右向左读相同，例如 `abba`。

子串必须连续。如果有多个同样长的最长答案，返回其中任意一个即可。返回字符串本身，不是它的长度。

**数据范围与约定**

- `1 <= s.length <= 1000`
- `s` 仅由数字和英文字母组成

**示例**

`s="cabbad"` 返回 `"abba"`，这是以两个 `b` 之间为中心的偶数长度回文。

#### 解法：枚举中心，向两边扩展

回文有两类中心：一个字符，或相邻两个字符之间。枚举所有中心，只要两侧字符相同就继续向外扩展，直到不同或越界。记录扩展出的最长区间，最后返回对应子串。

```python
class Solution:

    def longestPalindrome(self, s):
        start = length = 0
        for center in range(len(s)):
            for left, right in ((center, center), (center, center + 1)):
                while left >= 0 and right < len(s) and (s[left] == s[right]):
                    left -= 1
                    right += 1
                current = right - left - 1
                if current > length:
                    start, length = (left + 1, current)
        return s[start:start + length]
```

**复杂度：** 时间 \(O(n^2)\)，额外空间 \(O(1)\)，输出子串另计；\(n\) 为字符串长度。

#### 补充：Manacher：利用回文的对称性

在字母间插入 `#`，例如 `"aba"` 变成 `"^#a#b#a#$"`，让奇、偶长度回文都能用单个中心处理；两端不同符号负责挡住越界扩展。

`radius[position]` 表示从中心到回文一端的字符数，包含中心。例如新串中的 `"#a#"` 半径为 2。若新中心处在已知回文内，就借用它的镜像中心半径，但最多借到已知右边界；剩余部分再向外比较。右边界只向右推进，因此总扩展次数为线性。

```python
class Solution:
    def longestPalindrome(self, s):
        expanded = '#'.join('^' + s + '$')
        radius = [0] * (len(expanded) - 2)
        radius[1] = 1
        center = right = best = 0
        for position in range(2, len(radius)):
            size = 1
            if position < right:
                mirror = 2 * center - position
                size = min(radius[mirror], right - position)
            while expanded[position - size] == expanded[position + size]:
                size += 1
                center, right = position, position + size
            radius[position] = size
            if size > radius[best]:
                best = position
        size = radius[best]
        start = (best - size) // 2
        stop = (best + size) // 2 - 1
        return s[start:stop]
```

**复杂度：** 时间 \(O(n)\)，空间 \(O(n)\)。

**注意：** `right` 是已知回文右端的后一位。代码最后把新串下标换回原串；题目只含字母数字，三个辅助符号不会与输入冲突。

**写法补充：** 原文的两个中心扩展版本仅在奇、偶中心的循环组织上不同。

### 最长公共子序列（LeetCode 1143）

中等 · [力扣原题](https://leetcode.cn/problems/longest-common-subsequence/) · [灵茶山艾府题解](https://leetcode.cn/problems/longest-common-subsequence/solutions/2133188/jiao-ni-yi-bu-bu-si-kao-dong-tai-gui-hua-lbz5/)

#### 题面

给定字符串 `text1` 和 `text2`，分别从中删除任意数量的字符，但不改变剩余字符的先后顺序。求两边能够得到的相同字符串的最大长度，也就是最长公共子序列长度。

选中的字符不必连续。如果完全没有共同字符，返回 0。只返回长度，不需要返回那条公共子序列。

**数据范围与约定**

- `1 <= text1.length, text2.length <= 1000`
- `text1` 和 `text2` 仅由小写英文字符组成。

**示例**

`text1="abcde"`、`text2="ace"`，返回 `3`，最长公共子序列为 `"ace"`。

#### 解法：比较两个前缀的末字符

记录两个字符串各取一段前缀时，最长公共子序列的长度。末字符相同，就取去掉两个末字符后的答案加一；不同，就分别尝试去掉其中一个末字符，取较大值。

用一行数组更新时，旧 `best[j]` 是上方，新 `best[j-1]` 是左方；另用 `diagonal` 保存旧的左上值，避免覆盖后丢失。

```python
class Solution:

    def longestCommonSubsequence(self, text1, text2):
        best = [0] * (len(text2) + 1)
        for a in text1:
            diagonal = 0
            for j, b in enumerate(text2, 1):
                above = best[j]
                if a == b:
                    best[j] = diagonal + 1
                else:
                    best[j] = max(best[j], best[j - 1])
                diagonal = above
        return best[-1]
```

**复杂度：** 时间 \(O(nm)\)，额外空间 \(O(m)\)；\(n,m\) 为两字符串长度。

#### 补充：记忆化比较两个前缀的末字符

`best(i,j)` 表示两个前缀的最长公共子序列长度。末字符相等时可以一起选，转到两个更短前缀再加一；不等时至少舍弃一个末字符，分别尝试后取最大。

```python
from functools import cache

class Solution:
    def longestCommonSubsequence(self, text1, text2):
        @cache
        def best(i, j):
            if i < 0 or j < 0:
                return 0
            if text1[i] == text2[j]:
                return best(i - 1, j - 1) + 1
            return max(best(i - 1, j), best(i, j - 1))
        return best(len(text1) - 1, len(text2) - 1)
```

**复杂度：** 时间、缓存 \(O(mn)\)，递归栈 \(O(m+n)\)。

#### 补充：二维公共子序列表

`dp[i][j]` 对应长度为 `i` 和 `j` 的两个前缀。末字符相同，从左上角加一；不同，取上方和左方较大值。首行首列为零，表示至少一个前缀为空。

```python
class Solution:
    def longestCommonSubsequence(self, text1, text2):
        dp = [[0] * (len(text2) + 1) for _ in range(len(text1) + 1)]
        for i, a in enumerate(text1, 1):
            for j, b in enumerate(text2, 1):
                if a == b:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[-1][-1]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(mn)\)。

#### 补充：两个数组保存相邻两行

转移只读取上一行的同列、上一列，以及当前行的左侧，因此两行轮流使用即可。当前行的零号位置始终为零，其余位置每轮从左到右完整覆盖。

```python
class Solution:
    def longestCommonSubsequence(self, text1, text2):
        rows = [[0] * (len(text2) + 1) for _ in range(2)]
        for i, a in enumerate(text1):
            previous, current = rows[i % 2], rows[(i + 1) % 2]
            for j, b in enumerate(text2, 1):
                if a == b:
                    current[j] = previous[j - 1] + 1
                else:
                    current[j] = max(previous[j], current[j - 1])
        return rows[len(text1) % 2][-1]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(n)\)，n 为第二个字符串长度。

**注意：** 主解法进一步压成一行，并额外保存旧的左上角值。

### 编辑距离（LeetCode 72）

中等 · [力扣原题](https://leetcode.cn/problems/edit-distance/) · [灵茶山艾府题解](https://leetcode.cn/problems/edit-distance/solutions/2133222/jiao-ni-yi-bu-bu-si-kao-dong-tai-gui-hua-uo5q/)

#### 题面

给定字符串 `word1` 和 `word2`，你可以对 `word1` 执行三种操作：插入一个字符、删除一个字符、把一个字符替换成另一个。求将它变成 `word2` 至少需要多少次操作。

每次只能处理一个字符，每次操作的代价都算 1。允许某个输入为空字符串；返回最少操作次数。

**数据范围与约定**

- `0 <= word1.length, word2.length <= 500`
- `word1` 和 `word2` 由小写英文字母组成

**示例**

`"cat"` 变成 `"cut"` 只需替换 `a`，返回 `1`；空串变成 `"abc"` 需插入三次。

#### 解法：比较插入、删除、替换的代价

记录把源字符串的前缀变成目标前缀所需的最少次数。末字符相同就沿用左上方答案；不同则比较删除源末字符、插入目标末字符、替换源末字符三种情况，各加一次操作，取最小值。

一行更新中，这三个旧问题分别是 `above`、`best[j-1]`、`diagonal`。空前缀的答案等于另一前缀长度，表示全部插入或删除。

```python
class Solution:

    def minDistance(self, word1, word2):
        best = list(range(len(word2) + 1))
        for i, a in enumerate(word1, 1):
            diagonal = best[0]
            best[0] = i
            for j, b in enumerate(word2, 1):
                above = best[j]
                if a == b:
                    best[j] = diagonal
                else:
                    best[j] = 1 + min(above, best[j - 1], diagonal)
                diagonal = above
        return best[-1]
```

**复杂度：** 时间 \(O(nm)\)，额外空间 \(O(m)\)；\(n,m\) 为两字符串长度，采用一维滚动写法。

#### 补充：记忆化处理两个前缀的末字符

末字符相同就一起略过。不同则比较删除、插入、替换三种操作所对应的更短前缀问题，再加一次操作。某前缀为空时，只能逐个插入或删除另一个前缀的字符。

```python
from functools import cache

class Solution:
    def minDistance(self, word1, word2):
        @cache
        def distance(i, j):
            if i < 0:
                return j + 1
            if j < 0:
                return i + 1
            if word1[i] == word2[j]:
                return distance(i - 1, j - 1)
            return 1 + min(distance(i - 1, j), distance(i, j - 1), distance(i - 1, j - 1))
        return distance(len(word1) - 1, len(word2) - 1)
```

**复杂度：** 时间、缓存 \(O(mn)\)，递归栈 \(O(m+n)\)。

#### 补充：二维编辑距离表

`dp[i][j]` 是把 `word1` 的前 `i` 个字符变成 `word2` 前 `j` 个字符的最少操作数。首行和首列分别是全部插入和全部删除；字符相同时用左上角，否则取上、左、左上三个状态的最小值加一。

```python
class Solution:
    def minDistance(self, word1, word2):
        dp = [[0] * (len(word2) + 1) for _ in range(len(word1) + 1)]
        dp[0] = list(range(len(word2) + 1))
        for i, a in enumerate(word1, 1):
            dp[i][0] = i
            for j, b in enumerate(word2, 1):
                if a == b:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[-1][-1]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(mn)\)。

#### 补充：两个数组轮流计算编辑距离

保留上一行和当前行即可完成转移。每轮先把当前行第零列设为当前前缀长度，表示删空所需次数；再从左到右覆盖其他列，最后按字符串长度的奇偶选择结果行。

```python
class Solution:
    def minDistance(self, word1, word2):
        rows = [list(range(len(word2) + 1)), [0] * (len(word2) + 1)]
        for i, a in enumerate(word1):
            previous, current = rows[i % 2], rows[(i + 1) % 2]
            current[0] = i + 1
            for j, b in enumerate(word2, 1):
                if a == b:
                    current[j] = previous[j - 1]
                else:
                    current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        return rows[len(word1) % 2][-1]
```

**复杂度：** 时间 \(O(mn)\)，空间 \(O(n)\)，n 为第二个字符串长度。

**注意：** 与一行版本同为线性空间，但上一行仍完整保留，更容易看出状态对应关系。


## 技巧

### 只出现一次的数字（LeetCode 136）

简单 · [力扣原题](https://leetcode.cn/problems/single-number/) · [灵茶山艾府题解](https://leetcode.cn/problems/single-number/solutions/2481594/li-yong-yi-huo-de-xing-zhi-fu-ti-dan-pyt-oizc/)

#### 题面

给定非空整数数组 `nums`。其中只有一个数出现一次，其他每个数都恰好出现两次。找出并返回这个只出现一次的数。

要求时间复杂度为 \(O(n)\)，并且只使用 \(O(1)\) 额外空间。

**数据范围与约定**

- `1 <= nums.length <= 3 * 10^4`
- `-3 * 10^4 <= nums[i] <= 3 * 10^4`
- 除了某个元素只出现一次以外，其余每个元素均出现两次。

**示例**

`[6,2,6,9,2]` 返回 `9`，两个 `6` 和两个 `2` 分别抵消。

#### 解法：把所有数依次异或

异或运算 `^` 满足：同一个数异或自身得到零，零异或任何数仍是这个数，而且运算顺序不影响结果。因此全部数异或后，成对出现的值都抵消，只剩那个出现一次的数。

```python
class Solution:

    def singleNumber(self, nums):
        result = 0
        for value in nums:
            result ^= value
        return result
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

### 多数元素（LeetCode 169）

简单 · [力扣原题](https://leetcode.cn/problems/majority-element/) · [灵茶山艾府题解](https://leetcode.cn/problems/majority-element/solutions/3744717/on-mo-er-tou-piao-fa-yan-jin-zheng-ming-ww1zv/)

#### 题面

给定非空整数数组 `nums`，找出出现次数严格超过数组长度一半的那个数，并返回它。

题目保证这样的数一定存在。

**数据范围与约定**

- `n == nums.length`
- `1 <= n <= 5 * 10^4`
- `-10^9 <= nums[i] <= 10^9`
- 输入保证数组中一定有一个多数元素。

**进阶要求**

- 尝试设计时间复杂度为 \(O(n)\)、空间复杂度为 \(O(1)\) 的算法解决此问题。

**示例**

`[2,1,2,3,2]` 返回 `2`，它出现三次，超过长度五的一半。

#### 解法：不同值两两抵消，保留候选

`candidate` 是当前候选，`votes` 是尚未抵消的次数。次数为零时选择新候选；同值加一，异值减一，相当于删去一对不同元素。多数元素比其余所有元素加起来还多，无论怎样配对抵消，最后留下的候选一定是它。

```python
class Solution:

    def majorityElement(self, nums):
        candidate = None
        votes = 0
        for value in nums:
            if votes == 0:
                candidate = value
            votes += 1 if value == candidate else -1
        return candidate
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

### 颜色分类（LeetCode 75）

中等 · [力扣原题](https://leetcode.cn/problems/sort-colors/) · [灵茶山艾府题解](https://leetcode.cn/problems/sort-colors/solutions/3679069/on-cha-ru-pai-xu-jian-ji-xie-fa-pythonja-zk60/)

#### 题面

给定只含 0、1、2 的数组 `nums`，这三个数分别表示红、白、蓝三种颜色。重新排列数组，使所有 0 在前、所有 1 居中、所有 2 在后。

直接修改原数组，不能调用排序库函数。

**数据范围与约定**

- `n == nums.length`
- `1 <= n <= 300`
- `nums[i] 为 0、1 或 2`

**进阶要求**

- 你能想出一个仅使用常数空间的一趟扫描算法吗？

**示例**

`[2,0,1]` 改为 `[0,1,2]`，三种颜色按红、白、蓝排列。

#### 解法：依次写入 2、1、0，扩展有序前缀

`zeros` 记录已处理的零的数量，`zeros_and_ones` 记录零和一的总数。先保存当前原值，再把当前位置写成 `2`；原值不为 `2`，就在零和一区域末尾写 `1`；原值为 `0`，再在零区域末尾写 `0`。按这个顺序覆盖并更新计数，已处理部分始终有序。

```python
class Solution:

    def sortColors(self, nums):
        zeros = zeros_and_ones = 0
        for i in range(len(nums)):
            value = nums[i]
            nums[i] = 2
            if value <= 1:
                nums[zeros_and_ones] = 1
                zeros_and_ones += 1
            if value == 0:
                nums[zeros] = 0
                zeros += 1
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

### 下一个排列（LeetCode 31）

中等 · [力扣原题](https://leetcode.cn/problems/next-permutation/) · [灵茶山艾府题解](https://leetcode.cn/problems/next-permutation/solutions/3621022/jiao-ni-cong-ling-kai-shi-si-kao-zhe-ti-9qfrq/)

#### 题面

给定整数数组 `nums`，用它原有的全部元素重新排列，得到字典序中恰好排在当前排列后面的那一个。字典序比较时，从左到右找到第一个不同位置，那个位置数值更大的排列排在后面。

如果当前排列已经是最大的，就改成最小的递增排列。数组可以包含重复值。必须原地修改，只使用常数额外空间，不需要返回新数组。

**数据范围与约定**

- `1 <= nums.length <= 100`
- `0 <= nums[i] <= 100`

**示例**

`[1,3,2]` 的下一个排列是 `[2,1,3]`；`[3,2,1]` 已经最大，改成 `[1,2,3]`。

#### 解法：尽量靠右增大一位，再把后缀变最小

从右往左找第一个比右邻小的位置。它右侧已经按非递增排列，仅重排后缀无法变大，所以必须增大这一位。再从右找第一个比它大的数交换，最后反转后缀，使后缀变成最小的升序。若找不到可增大的位置，整个数组已经最大，全部反转即可。

```python
class Solution:

    def nextPermutation(self, nums):
        pivot = len(nums) - 2
        while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
            pivot -= 1
        if pivot >= 0:
            candidate = len(nums) - 1
            while nums[candidate] <= nums[pivot]:
                candidate -= 1
            nums[pivot], nums[candidate] = (nums[candidate], nums[pivot])
        left, right = (pivot + 1, len(nums) - 1)
        while left < right:
            nums[left], nums[right] = (nums[right], nums[left])
            left += 1
            right -= 1
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n\) 为数组长度。

### 寻找重复数（LeetCode 287）

中等 · [力扣原题](https://leetcode.cn/problems/find-the-duplicate-number/) · [灵茶山艾府题解](https://leetcode.cn/problems/find-the-duplicate-number/solutions/3797843/yong-ji-huan-shu-li-jie-zuo-fa-tong-142-tkoc2/)

#### 题面

给定长度为 `n+1` 的整数数组 `nums`，所有数都在 1 到 `n` 之间。只有一个数出现不止一次，其余数各出现一次，找出并返回这个重复数。

重复数可能出现两次以上。不能修改输入数组，并且只能使用常数额外空间。

**数据范围与约定**

- `1 <= n <= 10^5`
- `nums.length == n + 1`
- `1 <= nums[i] <= n`
- `nums` 中 只有一个整数 出现 两次或多次 ，其余整数均只出现 一次

**进阶要求**

- 如何证明 `nums` 中至少存在一个重复的数字?
- 你可以设计一个线性级时间复杂度 \(O(n)\) 的解决方案吗？

**示例**

`[2,3,1,3]` 返回 `3`；按下标前进是 `0→2→1→3→3…`，入口 `3` 对应重复值。

#### 解法：把数组值当作下一个下标，寻找环入口

把下标 `i` 的下一站定义为 `nums[i]`。从零出发始终能继续，但不会回到零；位置有限，最终必然进入环。环入口既被环外的前一个位置指向，又被环内的前一个位置指向，说明至少两个数组元素等于这个入口下标。

先用快慢指针找相遇点，再让一指针回到零，两者同速前进，重新相遇处就是重复数。

```python
class Solution:

    def findDuplicate(self, nums):
        slow = nums[0]
        fast = nums[nums[0]]
        while slow != fast:
            slow = nums[slow]
            fast = nums[nums[fast]]
        entrance = 0
        while entrance != slow:
            entrance = nums[entrance]
            slow = nums[slow]
        return entrance
```

**复杂度：** 时间 \(O(n)\)，额外空间 \(O(1)\)；\(n+1\) 为数组长度。


## 整理说明

覆盖范围为本资料链接的 100 篇题解：原文 238 个 Python 代码块整理为 200 份完整实现，另有 33 份等价写法合并说明。教学慢方法、时间与空间的取舍、输入修改行为均在对应方法旁注明。

另有 5 段演示或扩展不作为本题提交版本：两数相加的链表遍历、回文链表的反向打印、组合总和的搜索规模验证、搜索二维矩阵 II 的测试数据构造、最长递增子序列的具体序列恢复。

代码已对照具体原文版本核验，并做本地行为比较；未实际提交力扣。资料核对日期：2026-10-03。