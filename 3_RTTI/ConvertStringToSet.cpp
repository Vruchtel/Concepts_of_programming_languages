#include "ConvertStringToSet.h"

void ConvertStringToSet(std::string original, std::set<std::string> &resultSet) {
	std::string str = original.substr(1, original.length() - 2);
	if (str.length() != 0) {
		int pos = 0;
		while (pos != std::string::npos) {
			pos = str.find(",");
			std::string curStr = str.substr(0, pos);
			if (int spacePos = curStr.find(" ") != std::string::npos) {
				curStr = curStr.substr(spacePos);
			}
			resultSet.insert(curStr);
			str = str.substr(pos + 1);
		}
	}
}