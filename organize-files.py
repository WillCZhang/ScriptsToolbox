import argparse
import os

PREFIX = "prefix"
SUFFIX = "suffix"
RULES = [PREFIX, SUFFIX]

def findFileGroupByRule(file, todo, rule):
    if rule == PREFIX:
        return findFileGroup(file, todo)
    elif rule == SUFFIX:
        groupName, fileGroup = findFileGroup(file[::-1], reverseEveryStringInList(todo))
        return groupName[::-1], reverseEveryStringInList(fileGroup)


def findFileGroup(file, filesToOrganize):
    """
    This function returns a group of file names, which the similarity of file names inside the group is maximized.

    @param file: str - file name to be compared with
    @param filesToOrganize: a set of file names to be organized
    @return: str - group name for these files, or file name if no suitable pattern was found
    @return: str[] - a list of file names
    """
    prefix, files = longestPrefix(file, filesToOrganize)
    if len(files) == 0:
        return file, [file]
    suffix, tempFiles = longestPrefix(file[::-1], reverseEveryStringInList(files))
    suffix = suffix[::-1]
    # update files only when at least one string is identified
    files = reverseEveryStringInList(tempFiles) if len(tempFiles) > 0 else files
    groupName = prefix + suffix
    # handling egde cases for group names with white spaces only
    # TODO: this will cause issue where two group names are "a b" and "ab"
    groupName = groupName.replace(" ", "")
    if len(groupName) == 0:
        groupName = file
        del files[:]
    files.append(file)
    return groupName, files


def longestPrefix(string, strings):
    """
    This function returns a group of strings that have the longest prefix with the given string and that prefix.

    @param string: str - to compare with
    @param strings: str[] - a list of strings to look at
    @return: str - the longest prefix
    @return: str[] - a list of strings that have the longest prefix with the given string, or empty if none was found
    """
    strings = [i for i in strings if i != string]
    prefix = ""
    minPrefixLen = 1
    stringGroup = []
    for s in strings:
        start = stringDiff(string, s)
        if start == minPrefixLen:
            stringGroup.append(s)
        elif start > minPrefixLen:
            minPrefixLen = start
            prefix = string[:start]
            del stringGroup[:]
            stringGroup.append(s)
    return prefix, stringGroup


def stringDiff(s1, s2):
    """
    This function compare two strings, and return two indices in string 1 where the diff substring of the two strings starts.
    e.g. for abc & abd, it will return 1

    @param s1: string1
    @param s2: string2
    @return: the start index of the diff substring in s1
    """
    start1 = start2 = 0
    while start1 < len(s1) and start2 < len(s2):
        if s1[start1] != s2[start2]:
            break
        start1 += 1
        start2 += 1
    return start1


# def reduceGroups(groups):
#     groups = {}
#     for group in groups:
        


def reverseEveryStringInList(l):
    return list(map(lambda s: s[::-1], l))


def organizFiles(fileGroup):
    # TODO
    raise Exception("Run is not implemented yet!")


def main():
    description = """Organize files that have common name patterns, 
                    so all the files that are named in pattern <PREFIX>...<SUFFIX> 
                    will be organized into folders <PREFIX><SUFFIX>.

                    By default this tool will only describe what is going to happen just to be safe,
                    run with "--run" to actually performance the organizing process.

                    Note: only the name pattern that matches with more than one file will be organized.
                    """
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("--ignore-extension", type=bool, default=False, help="will ignore file extensions -- not implemented")
    parser.add_argument("--path", type=str, default=os.getcwd(), help="indicates which directory to be organized")
    parser.add_argument("--prefix", type=str, default="", help="will only organize files with this prefix")
    parser.add_argument("--rule", type=str, default=PREFIX, help="indicates organizing rules, must be one of " + str(RULES))
    parser.add_argument("--run", type=bool, default=False, help="will actually perform the file organizing process -- not implemented")
    parser.add_argument("--suffix", type=str, default="", help="will only organize files with this suffix")
    args = parser.parse_args()
    if args.rule not in RULES:
        raise Exception("The rule %s is not defined!", args.rule)
    # prefix & suffix helpers 
    containPrefixSuffix = lambda filename: filename.find(args.prefix) == 0 and filename.rfind(args.suffix) == len(filename) - len(args.suffix)
    removePrefixSuffix = lambda filename: filename[len(args.prefix):] if len(args.suffix) == 0 else filename[len(args.prefix):][:-len(args.suffix)]
    addPrefixSuffix = lambda filename: args.prefix + filename + args.suffix
    # finding files under the give path at a give path
    filesToOrganize = []
    for root, dirs, files in os.walk(args.path):
        if root == args.path:
            filesToOrganize = list(filter(containPrefixSuffix, files))
            break
    # start organizing
    # Remove & recover the prefx & suffix, so they won't affect the calculations
    # TODO
    file = removePrefixSuffix(file)
    todo = set(map(removePrefixSuffix, todo))
    groups = {}
    todo = set(filesToOrganize)
    for file in filesToOrganize:
        # try to minize each group to a serveal subgroups
        if file in todo:
            # abstract to a helper to continue organizing
            groupName, fileGroup = findFileGroupByRule(file, todo, args.rule)
            if groupName in groups and (len(groups[groupName]) != len(fileGroup) or len([i for i in groups[groupName] if i not in fileGroup]) != 0):
                raise Exception("Group members should be the same. Needs investigation.\n Group1: %s \n Group2: %s"%(str(groups[groupName]),str(fileGroup)))
            if groupName not in groups:
                groups[groupName] = fileGroup
            todo = todo - fileGroup
    groupName = addPrefixSuffix(groupName)
    fileGroup = set(map(addPrefixSuffix, fileGroup))
    # group = reduceGroups(group)
    unrecognized = []
    counter = 0 # TODO
    organized = {""}
    for groupName in groups:
        group = []
        for file in groups[groupName]:
            if file not in organized:
                group.append(file)
                organized.add(file)
        counter += len(group)

        # organize file only when a suitable name pattern were found among the files
        if len(group) > 1 and len(group) != len(filesToOrganize):
            print("============================================")
            print("Found a file group named '%s'" % groupName)
            print("Files inside this group are %s" % str(group))
            if args.run:
                organizFiles(group)
        else:
            unrecognized = [i for i in unrecognized or group]
    print("============================================")
    # assert counter == len(filesToOrganize)
    if len(unrecognized) != 0:
        print("Files that have no suitable name pattern recognized: %s" % str(unrecognized))
    print("Finished organizing files.")


main()
