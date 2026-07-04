from builtins import range

import maya.OpenMaya as om

import json

import csv


__all__ = ['profilerToJSON', 'profilerToCSV', 'profilerFormatJSON']


def profilerToJSON(fileName, useIndex, durationMin):
    """
    fileName : name of file to write to disk
    useIndex : write events using index lookup to category and name lists
    durationMin : only write out events which have at least this minimum time duration

    Description:
    Sample code to extract profiler information and write to file in JSON format

    Example usage:
        > profilerToJSON('profiler_indexed.json', True, 0.0)  # Index without a duration clamp
        > profilerToJSON('profiler_nonIndexed.json', False, 10.0)  # Non-Indexed with duration clamp
    """

    stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)

    eventCount = om.MProfiler.getEventCount()
    if eventCount == 0:
        return

    file = open(fileName, "w")
    if not file:
        return

    file.write("{\n")

    file.write("\t\"version\": 1,\n")

    file.write("\t\"eventCount\": " + str(eventCount) + ",\n")

    file.write("\t\"cpuCount\": " + str(om.MProfiler.getNumberOfCPUs()) + ",\n")

    categories = []
    om.MProfiler.getAllCategories(categories)
    asciiString = json.dumps(categories, True, True)
    if useIndex:
        file.write("\t\"categories\": " + asciiString + ",\n")

    nameDict = {}
    for i in range(0, eventCount, 1):
        eventName = om.MProfiler.getEventName(i)
        eventName = eventName.decode('ascii', 'replace')
        eventName = stripped(eventName)
        if eventName not in nameDict:
            nameDict[eventName] = len(nameDict)
    if useIndex:
        nameString = json.dumps(list(nameDict.keys()), True, True)
        file.write('\t"eventNames" : ' + nameString + ",\n")

    file.write('\t"events": [\n')
    dumped = False
    eventsWritten = 0
    for i in range(0, eventCount):

        duration = om.MProfiler.getEventDuration(i)
        if duration > durationMin:
            eventsWritten = eventsWritten + 1

            eventTime = om.MProfiler.getEventTime(i)
            eventName = om.MProfiler.getEventName(i)
            eventName = eventName.decode('ascii', 'replace')
            eventName = stripped(eventName)
            if useIndex:
                eventNameIndex = list(nameDict.keys()).index(eventName)

            description = ''
            if om.MProfiler.getDescription(i):
                description = om.MProfiler.getDescription(i)

            eventCategory = om.MProfiler.getEventCategory(i)
            eventCategoryName = om.MProfiler.getCategoryName(eventCategory)
            if useIndex:
                eventCatagoryIndex = categories.index(eventCategoryName)

            threadDuration = om.MProfiler.getThreadDuration(i)

            threadId = om.MProfiler.getThreadId(i)

            cpuId = om.MProfiler.getCPUId(i)

            colorId = om.MProfiler.getColor(i)

            if dumped:
                file.write('\t,{ ')
            else:
                file.write('\t{ ')
            dumped = True
            file.write('"time" : ' + str(eventTime) + ', ')
            if useIndex:
                file.write('"nameIdx" : ' + str(eventNameIndex) + ', ')
            else:
                file.write('"name" : "' + eventName + '", ')
            file.write('"desc" : "' + str(description) + '", ')
            if useIndex:
                file.write('"catIdx" : ' + str(eventCatagoryIndex) + ', ')
            else:
                file.write('"category" : "' + eventCategoryName + '", ')
            file.write('"duration" : ' + str(duration) + ', ')
            file.write('"tDuration" : ' + str(threadDuration) + ', ')
            file.write('"tId" : ' + str(threadId) + ', ')
            file.write('"cpuId" : ' + str(cpuId) + ', ')
            file.write('"colorId" : ' + str(colorId) + '')
            file.write('\t}\n')

    file.write("\t],\n")
    file.write("\t\"eventsWritten\": " + str(eventsWritten) + "\n")
    file.write("}\n")
    file.close()


def profilerFormatJSON(fileName, fileName2):
    """
    fileName : name of file to read
    fileName2 : name of file to write to

    Description:
    Simple utility code to read a JSON file sort and format it before
    writing to a secondary file.

    Example:
        > profilerFormatJSON('profilerIn.json', 'profilerFormatted.json')
    """
    file = open(fileName, "r")
    if not file:
        return

    result = json.load(file)
    file.close()

    dump = json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))

    file2 = open(fileName2, "w")
    if not file2:
        return

    file2.write(dump)
    file2.close()


def profilerToCSV(fileName, durationMin):
    """
    fileName : name of file to write to disk
    useIndex : write events using index lookup to category and name lists
    durationMin : only write out events which have at least this minimum time duration

    Description:
    Sample to output profiler event information only to CSV format.

    Example:
        > profilerToCSV('profiler.csv', 0.0)
    """

    stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)

    eventCount = om.MProfiler.getEventCount()
    if eventCount == 0:
        return

    file = open(fileName, "w")
    if not file:
        return

    csvWriter = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)

    head = ('Event Time', 'Event Name', 'Description', 'Event Category',
            'Duration', 'Thread Duration', 'Thread Id', 'CPU Id', 'Color Id')
    csvWriter.writerow(head)

    for i in range(0, eventCount):

        duration = om.MProfiler.getEventDuration(i)
        if duration > durationMin:

            eventTime = om.MProfiler.getEventTime(i)
            eventName = om.MProfiler.getEventName(i)
            eventName = eventName.decode('ascii', 'replace')
            eventName = stripped(eventName)

            description = ''
            if om.MProfiler.getDescription(i):
                description = om.MProfiler.getDescription(i)

            eventCategory = om.MProfiler.getEventCategory(i)
            eventCategoryName = om.MProfiler.getCategoryName(eventCategory)

            threadDuration = om.MProfiler.getThreadDuration(i)

            threadId = om.MProfiler.getThreadId(i)

            cpuId = om.MProfiler.getCPUId(i)

            colorId = om.MProfiler.getColor(i)

            row = (eventTime, eventName, description, eventCategoryName,
                   duration, threadDuration, threadId, cpuId, colorId)

            csvWriter.writerow(row)

    file.close()


def initializePlugin(obj):
    obj


def uninitializePlugin(obj):
    obj
